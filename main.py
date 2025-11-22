"""
Main script for documentation validation.
UPDATED: Now processes ALL Excel files from Google Drive folder
Downloads multiple Excel files, validates documentation references,
and creates reports with validation results for each file.
"""

from drive_utils import (
    authenticate_drive_api,
    download_all_excel_files,
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
    3. Download ALL Excel files from the folder
    4. Process and validate each file
    5. Generate outputs with validation results
    """
    print("=" * 60)
    print("Documentation Validator - BATCH MODE")
    print("=" * 60 + "\n")

    # Read the API key and folder ID from the link.txt file
    api_key, folder_id = read_credentials_file(LINK_FILE)

    if not api_key or not folder_id:
        print("Error: API Key or Folder ID not found in link.txt.")
        return None

    # Authenticate with Google Drive API using the API key
    print("🔐 Authenticating with Google Drive...")
    drive_service = authenticate_drive_api(api_key)

    # Download all Excel files from the folder
    print("\n🔍 Searching for Excel files in folder...")
    downloaded_files = download_all_excel_files(drive_service, folder_id)

    if not downloaded_files:
        print("\n❌ No Excel files found to process.")
        return None

    # Process each downloaded file
    print("\n" + "=" * 60)
    print(f"PROCESSING {len(downloaded_files)} FILE(S)")
    print("=" * 60)

    processed_files = []
    failed_files = []

    for i, file_info in enumerate(downloaded_files, 1):
        print(f"\n{'='*60}")
        print(f"FILE {i}/{len(downloaded_files)}: {file_info['name']}")
        print(f"{'='*60}")

        try:
            # Process the Excel file
            processed_file = process_excel(file_info['path'])

            if processed_file:
                processed_files.append({
                    'original': file_info['name'],
                    'output': processed_file
                })
                print(f"\n✅ Successfully processed: {file_info['name']}")
            else:
                failed_files.append(file_info['name'])
                print(f"\n❌ Failed to process: {file_info['name']}")

        except Exception as e:
            failed_files.append(file_info['name'])
            print(f"\n❌ Error processing {file_info['name']}: {str(e)}")
            import traceback
            traceback.print_exc()

    # Final summary
    print("\n" + "=" * 60)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   Total files: {len(downloaded_files)}")
    print(f"   ✅ Successful: {len(processed_files)}")
    print(f"   ❌ Failed: {len(failed_files)}")

    if processed_files:
        print(f"\n✅ Successfully processed files:")
        for i, file in enumerate(processed_files, 1):
            print(f"   {i}. {file['original']}")
            print(f"      → {file['output']}")

    if failed_files:
        print(f"\n❌ Failed files:")
        for i, file in enumerate(failed_files, 1):
            print(f"   {i}. {file}")

    print("\n" + "=" * 60)

    return processed_files


if __name__ == "__main__":
    processed_files = main()