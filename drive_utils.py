"""
Google Drive utilities for downloading files.
UPDATED: Now supports downloading multiple Excel files from a folder
FIXED: Removed strict MIME type filtering to catch all .xlsx files
"""

import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from doc_validator.config import DATA_FOLDER


def authenticate_drive_api(api_key):
    """
    Authenticate with Google Drive API using API Key.

    Args:
        api_key: Google Drive API key

    Returns:
        drive_service: Authenticated Google Drive service
    """
    drive_service = build('drive', 'v3', developerKey=api_key)
    return drive_service


def get_all_excel_files_from_folder(drive_service, folder_id):
    """
    Get all Excel file IDs from the folder.
    FIXED: Now gets ALL files and filters by extension instead of MIME type.

    Args:
        drive_service: Authenticated Google Drive service
        folder_id: Google Drive folder ID

    Returns:
        list: List of dictionaries containing file info [{'id': ..., 'name': ...}, ...]
    """
    # FIXED: Get ALL files from folder (no MIME type filter)
    query = f"'{folder_id}' in parents and trashed=false"

    try:
        results = drive_service.files().list(
            q=query,
            fields="files(id, name, mimeType)",
            orderBy="name"
        ).execute()

        all_files = results.get('files', [])

        if not all_files:
            print('No files found in the folder.')
            return []

        # Filter for Excel files by extension
        excel_files = []
        for file in all_files:
            name = file.get('name', '').lower()
            if name.endswith('.xlsx') or name.endswith('.xls'):
                excel_files.append(file)

        if not excel_files:
            print(f'No Excel files found in the folder.')
            print(f'Found {len(all_files)} total file(s), but none are .xlsx or .xls')
            return []

        print(f"\n📁 Found {len(excel_files)} Excel file(s) in folder:")
        for i, file in enumerate(excel_files, 1):
            print(f"   {i}. {file['name']}")

        return excel_files

    except Exception as e:
        print(f"❌ Error accessing Google Drive folder: {str(e)}")
        return []


def get_file_id_from_folder(drive_service, folder_id):
    """
    LEGACY: Get the first file ID from the folder.
    Kept for backward compatibility.

    Args:
        drive_service: Authenticated Google Drive service
        folder_id: Google Drive folder ID

    Returns:
        file_id: ID of the first file in the folder, or None if no files found
    """
    results = drive_service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name)"
    ).execute()

    files = results.get('files', [])
    if not files:
        print('No files found in the folder.')
        return None

    file_id = files[0]['id']
    print(f"File found: {files[0]['name']} with ID: {file_id}")
    return file_id


def download_file_from_drive(drive_service, file_id, wp_value, file_name=None):
    """
    Download file from Google Drive to a specific folder.

    Args:
        drive_service: Authenticated Google Drive service
        file_id: Google Drive file ID to download
        wp_value: Work package value for folder naming
        file_name: Optional custom filename (if None, uses default naming)

    Returns:
        file_path: Path to the downloaded file
    """
    # Create folder if it doesn't exist
    wp_folder = os.path.join(DATA_FOLDER, wp_value)
    os.makedirs(wp_folder, exist_ok=True)

    # Define file path for the downloaded file
    if file_name:
        file_path = os.path.join(wp_folder, file_name)
    else:
        file_path = os.path.join(wp_folder, f'WP_{wp_value}_RAW.xlsx')

    # Download the file
    try:
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.FileIO(file_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

        print(f"   ✓ Downloaded to: {file_path}")
        return file_path

    except Exception as e:
        print(f"   ❌ Error downloading file: {str(e)}")
        return None


def download_all_excel_files(drive_service, folder_id):
    """
    Download all Excel files from a Google Drive folder.

    Args:
        drive_service: Authenticated Google Drive service
        folder_id: Google Drive folder ID

    Returns:
        list: List of downloaded file paths
    """
    # Get all Excel files
    files = get_all_excel_files_from_folder(drive_service, folder_id)

    if not files:
        return []

    downloaded_files = []

    print(f"\n📥 Downloading {len(files)} file(s)...\n")

    for i, file in enumerate(files, 1):
        print(f"[{i}/{len(files)}] Downloading: {file['name']}")

        # Use temp_download folder for downloads
        file_path = download_file_from_drive(
            drive_service,
            file['id'],
            'temp_download',
            file['name']  # Keep original filename
        )

        if file_path:
            downloaded_files.append({
                'path': file_path,
                'name': file['name'],
                'id': file['id']
            })
        else:
            print(f"   ⚠️  Skipping file due to download error")

    print(f"\n✓ Downloaded {len(downloaded_files)} file(s) successfully!")

    if len(downloaded_files) < len(files):
        print(f"⚠️  {len(files) - len(downloaded_files)} file(s) failed to download")

    return downloaded_files


def read_credentials_file(filename):
    """
    Read API key and folder ID from credentials file.

    Args:
        filename: Path to credentials file (e.g., 'link.txt')

    Returns:
        tuple: (api_key, folder_id) or (None, None) if not found
    """
    try:
        with open(filename, 'r') as file:
            content = file.readlines()

        api_key = None
        folder_id = None

        for line in content:
            if line.startswith("GG_API_KEY="):
                api_key = line.split('=')[1].strip()
            elif line.startswith("GG_FOLDER_ID="):
                folder_id = line.split('=')[1].strip()

        return api_key, folder_id

    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return None, None