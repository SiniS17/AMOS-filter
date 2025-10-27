import os
import pandas as pd
import shutil
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import re
from datetime import datetime

# Reason dictionary
reasons_dict = {
    "valid": "Valid documentation",
    "ref": "Missing reference documentation",
    "rev": "Missing revision date"
}

# Keywords to search for in the "text" column
ref_keywords = ["AMM", "SRM", "CMM", "EMM", "SOPM", "SWPM", "IPD", "FIM", "TSM", "IPC", "SB", "AD", "NTO", "MEL", "NEF",
                "MME", "LMM"]
rev_keywords = ["REV", "EXP", "DEADLINE"]
invalid_characters = r'[\\/:*?"<>|]'  # Invalid characters for folder names
iaw_ref_per_keywords = ["IAW", "REF", "PER", "I.A.W"]  # Keywords for IAW_sym_keyword


# Function to authenticate with Google Drive API using API Key
def authenticate_drive_api(api_key):
    drive_service = build('drive', 'v3', developerKey=api_key)
    return drive_service


# Function to get the file ID from the folder (using the folder ID from link.txt)
def get_file_id_from_folder(drive_service, folder_id):
    results = drive_service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name)").execute()
    files = results.get('files', [])
    if not files:
        print('No files found in the folder.')
        return None
    file_id = files[0]['id']
    print(f"File found: {files[0]['name']} with ID: {file_id}")
    return file_id


# Function to download file from Google Drive to a specific folder
def download_file_from_drive(drive_service, file_id, wp_value):
    # Create folder if it doesn't exist
    wp_folder = os.path.join('DATA', wp_value)
    os.makedirs(wp_folder, exist_ok=True)

    # Define file path for the downloaded file
    file_path = os.path.join(wp_folder, f'WP_{wp_value}_RAW.xlsx')

    # Download the file
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    print(f"File downloaded to {file_path}")
    return file_path


# Function to get a sanitized file name from the "wp" column
def get_sanitized_filename(df):
    if 'wp' in df.columns:
        wp_value = df['wp'].dropna().iloc[0]
        sanitized_wp_value = re.sub(r'[^\w\s]', ' ', wp_value)
        sanitized_wp_value = sanitized_wp_value.replace(' ', '_')  # Replace spaces with underscores
        return f"WP_{sanitized_wp_value}"
    else:
        print("No 'wp' column found in the file.")
        return "WP_No_wp_found"


# Function to sanitize folder name (replace invalid characters with underscores)
def sanitize_folder_name(wp_value):
    if isinstance(wp_value, str):
        sanitized_wp_value = re.sub(invalid_characters, '_', wp_value)
        return sanitized_wp_value
    return "No_wp_found"


# Function to create a log file with the counts
def create_log_file(wp_value, output_file, missing_rev_count, missing_ref_count, total_errors):
    log_folder = os.path.join('DATA', wp_value, 'log')
    os.makedirs(log_folder, exist_ok=True)

    log_filename = os.path.join(log_folder, os.path.basename(output_file).replace('.xlsx', '.txt'))

    with open(log_filename, 'w') as log_file:
        log_file.write(f"Log for file: {output_file}\n")
        log_file.write(f"Total rows with missing revision date: {missing_rev_count}\n")
        log_file.write(f"Total rows with missing reference documentation: {missing_ref_count}\n")
        log_file.write(f"Total rows with errors: {total_errors}\n")

    print(f"Log file created at: {log_filename}")


# Function to check reference keywords and write the reasons into the "Reason" column
def check_ref_keywords(text):
    reasons = []

    if isinstance(text, str):
        # Skip phrases to allow valid documentation
        skip_phrases = [
            "GET ACCESS", "GAIN ACCESS", "GAINED ACCESS", "ACCESS GAINED",
            "SPARE ORDERED", "ORDERED SPARE"
        ]

        if any(phrase in text for phrase in skip_phrases):
            return reasons_dict["valid"]

        # Check if ref_keywords and IAW_sym_keywords are present together
        ref_keywords_pattern = r'\b(?:' + '|'.join(ref_keywords) + r')\b'  # Match whole words for ref_keywords
        iaw_ref_per_pattern = r'\b(?:' + '|'.join(iaw_ref_per_keywords) + r')\b'  # Match IAW, REF, PER

        # Missing reference documentation if no ref_keywords or IAW_sym_keywords
        if not re.search(ref_keywords_pattern, text, re.IGNORECASE) or not re.search(iaw_ref_per_pattern, text,
                                                                                     re.IGNORECASE):
            reasons.append(reasons_dict["ref"])

        # Check if "REV" is followed by a valid revision (any number is valid)
        rev_keywords_pattern = r'\bREV\s*\.?\s*(\d+)\b'  # Match REV followed by a number (e.g., REV 156, REV.156)
        if not re.search(rev_keywords_pattern, text, re.IGNORECASE):
            # Check if "EXP" or "DEADLINE" is followed by a valid date or time
            exp_deadline_pattern = r'\b(?:EXP|DEADLINE)\s*(\d{2}[A-Z]{3}\d{2}|\d{1,2}/\d{1,2}/\d{4}|\d{4})\b'  # Match EXP or DEADLINE followed by date or year
            if not re.search(exp_deadline_pattern, text, re.IGNORECASE):
                reasons.append(reasons_dict["rev"])

        # If there are no issues, it's valid documentation
        return ', '.join(reasons) if reasons else reasons_dict["valid"]

    return 'Error'

# Function to process the Excel file and add the "Reason" column based on ref_keywords
def process_excel(file_path):
    # Read the Excel file with row 1 as header
    df = pd.read_excel(file_path, engine='openpyxl', header=0)

    # Initialize counters
    missing_rev_count = 0
    missing_ref_count = 0
    total_errors = 0

    # Apply the check to each row in the "text" column and create a "Reason" column
    df['Reason'] = df['text'].apply(lambda text: check_ref_keywords(text))

    # Count errors
    missing_rev_count = df['Reason'].str.contains("Missing revision date").sum()
    missing_ref_count = df['Reason'].str.contains("Missing reference documentation").sum()
    total_errors = missing_rev_count + missing_ref_count

    # Get the folder name from the "wp" column and sanitize it
    wp_value = df['wp'].dropna().iloc[0] if 'wp' in df.columns else "No_wp_found"
    sanitized_folder_name = wp_value.replace(' ', '_')  # Sanitize wp value for folder name

    # Define the path where the processed file will be saved (in the same folder as the downloaded file)
    current_time = datetime.now().strftime("%I%p%M_%d_%m_%y").lower()
    output_file = os.path.join('DATA', sanitized_folder_name, f"WP_{sanitized_folder_name}_{current_time}.xlsx")

    # Create an ExcelWriter object with openpyxl engine
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, header=True)  # Write the data to Excel

        # Access the workbook and the sheet
        workbook = writer.book
        sheet = workbook.active

        # Add filter to the first row (header)
        sheet.auto_filter.ref = sheet.dimensions  # Automatically apply filter to the entire range (including header)

        # Save the workbook with the filter applied
        workbook.save(output_file)

    # Create a log file with error counts
    create_log_file(sanitized_folder_name, output_file, missing_rev_count, missing_ref_count, total_errors)

    print(f"Processed file saved at: {os.path.abspath(output_file)}")
    return output_file


# Main function to execute the process
def main():
    # Read the API key and folder ID from the link.txt file
    with open('link.txt', 'r') as file:
        content = file.readlines()

    api_key = None
    folder_id = None
    for line in content:
        if line.startswith("GG_API_KEY="):
            api_key = line.split('=')[1].strip()
        elif line.startswith("GG_FOLDER_ID="):
            folder_id = line.split('=')[1].strip()

    if not api_key or not folder_id:
        print("API Key or Folder ID not found in link.txt.")
        return

    # Authenticate with Google Drive API using the API key
    drive_service = authenticate_drive_api(api_key)

    # Get the file ID from the folder
    file_id = get_file_id_from_folder(drive_service, folder_id)
    if not file_id:
        print("No valid file found to download.")
        return

    # Download the file as a temp file and get wp_value from it
    wp_value = "example_wp"  # This will be extracted from the Excel file dynamically
    temp_file_path = download_file_from_drive(drive_service, file_id, wp_value)

    # Process the downloaded Excel file and save it in the same folder
    processed_file = process_excel(temp_file_path)
    return processed_file


if __name__ == "__main__":
    processed_file = main()
