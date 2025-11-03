"""
Excel file processing utilities.
"""

import os
import re
import pandas as pd
from datetime import datetime
from validators import check_ref_keywords
from config import DATA_FOLDER, LOG_FOLDER, INVALID_CHARACTERS


def sanitize_folder_name(wp_value):
    """
    Sanitize folder name (replace invalid characters with underscores).

    Args:
        wp_value: Work package value to sanitize

    Returns:
        str: Sanitized folder name
    """
    if isinstance(wp_value, str):
        cleaned_wp_value = re.sub(INVALID_CHARACTERS, '_', wp_value)
        return cleaned_wp_value
    return "No_wp_found"


def create_log_file(wp_value, output_file, missing_rev_count, missing_ref_count,
                    missing_ref_type_count, suspicious_rev_count, total_errors):
    """
    Create a log file with the validation counts.

    Args:
        wp_value: Work package value
        output_file: Path to the output Excel file
        missing_rev_count: Count of missing revision dates
        missing_ref_count: Count of missing reference documentation
        missing_ref_type_count: Count of missing reference types
        suspicious_rev_count: Count of suspicious revision formats
        total_errors: Total error count
    """
    log_folder = os.path.join(DATA_FOLDER, wp_value, LOG_FOLDER)
    os.makedirs(log_folder, exist_ok=True)

    log_filename = os.path.join(log_folder, os.path.basename(output_file).replace('.xlsx', '.txt'))

    with open(log_filename, 'w') as log_file:
        log_file.write(f"Log for file: {output_file}\n")
        log_file.write(f"=" * 60 + "\n\n")
        log_file.write(f"Total rows with missing revision date: {missing_rev_count}\n")
        log_file.write(f"Total rows with missing reference documentation: {missing_ref_count}\n")
        log_file.write(f"Total rows with missing reference type: {missing_ref_type_count}\n")
        log_file.write(f"Total rows with suspicious revision format: {suspicious_rev_count}\n")
        log_file.write(f"\nTotal rows with errors: {total_errors}\n")

    print(f"Log file created at: {log_filename}")


def process_excel(file_path):
    """
    Process the Excel file and add the "Reason" column based on validation.

    Args:
        file_path: Path to the Excel file to process

    Returns:
        str: Path to the processed output file
    """
    # Read the Excel file with row 1 as header
    df = pd.read_excel(file_path, engine='openpyxl', header=0)

    # Apply the validation to each row in the "text" column
    df['Reason'] = df['text'].apply(lambda text: check_ref_keywords(text))

    # Count errors
    missing_rev_count = df['Reason'].str.contains("Missing revision date", na=False).sum()
    missing_ref_count = df['Reason'].str.contains("Missing reference documentation", na=False).sum()
    missing_ref_type_count = df['Reason'].str.contains("Missing reference type", na=False).sum()
    suspicious_rev_count = df['Reason'].str.contains("Suspicious revision format", na=False).sum()

    # Total errors (count rows with any error, not the sum of all error types)
    total_errors = df[df['Reason'] != "Valid documentation"].shape[0]

    # Get the folder name from the "wp" column and sanitize it
    wp_value = df['wp'].dropna().iloc[0] if 'wp' in df.columns else "No_wp_found"
    cleaned_folder_name = wp_value.replace(' ', '_')

    # Define the path where the processed file will be saved
    current_time = datetime.now().strftime("%I%p%M_%d_%m_%y").lower()
    output_file = os.path.join(DATA_FOLDER, cleaned_folder_name,
                               f"WP_{cleaned_folder_name}_{current_time}.xlsx")

    # Create an ExcelWriter object with openpyxl engine
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, header=True)

        # Access the workbook and the sheet
        workbook = writer.book
        sheet = workbook.active

        # Add filter to the first row (header)
        sheet.auto_filter.ref = sheet.dimensions

        # Save the workbook with the filter applied
        workbook.save(output_file)

    # Create a log file with error counts
    create_log_file(cleaned_folder_name, output_file, missing_rev_count,
                    missing_ref_count, missing_ref_type_count, suspicious_rev_count,
                    total_errors)

    print(f"Processed file saved at: {os.path.abspath(output_file)}")
    return output_file