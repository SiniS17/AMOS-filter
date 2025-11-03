"""
Main script for documentation validation.
Downloads Excel file from Google Drive, validates documentation references,
and creates a report with validation results.
"""

from drive_utils import (
    authenticate_drive_api,
    get_file_id_from_folder,
    download_file_from_drive,
    read_credentials_file
)
from excel_utils import process_excel
from config import LINK_FILE


def main():
    """
    Main function to execute the documentation validation process.

    Steps:
    1. Read credentials from link.txt
    2. Authenticate with Google Drive
    3. Download the Excel file
    4. Process and validate the file
    5. Generate output with validation results
    """
    print("=" * 60)
    print("Documentation Validator")
    print("=" * 60 + "\n")

    # Read the API key and folder ID from the link.txt file
    api_key, folder_id = read_credentials_file(LINK_FILE)

    if not api_key or not folder_id:
        print("Error: API Key or Folder ID not found in link.txt.")
        return None

    # Authenticate with Google Drive API using the API key
    print("Authenticating with Google Drive...")
    drive_service = authenticate_drive_api(api_key)

    # Get the file ID from the folder
    print("Finding file in folder...")
    file_id = get_file_id_from_folder(drive_service, folder_id)
    if not file_id:
        print("Error: No valid file found to download.")
        return None

    # Download the file (using a placeholder wp_value, will be updated from file)
    print("Downloading file...")
    wp_value = "temp_download"
    temp_file_path = download_file_from_drive(drive_service, file_id, wp_value)

    # Process the downloaded Excel file and save it with validation results
    print("\nProcessing Excel file and validating documentation...")
    processed_file = process_excel(temp_file_path)

    print("\n" + "=" * 60)
    print("✓ Process completed successfully!")
    print("=" * 60)

    return processed_file


if __name__ == "__main__":
    processed_file = main()