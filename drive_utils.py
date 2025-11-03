"""
Google Drive utilities for downloading files.
"""

import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from config import DATA_FOLDER


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


def get_file_id_from_folder(drive_service, folder_id):
    """
    Get the file ID from the folder (using the folder ID from link.txt).

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


def download_file_from_drive(drive_service, file_id, wp_value):
    """
    Download file from Google Drive to a specific folder.

    Args:
        drive_service: Authenticated Google Drive service
        file_id: Google Drive file ID to download
        wp_value: Work package value for folder naming

    Returns:
        file_path: Path to the downloaded file
    """
    # Create folder if it doesn't exist
    wp_folder = os.path.join(DATA_FOLDER, wp_value)
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