# doc_validator/core/input_source_manager.py
"""
Manages loading Excel files from different sources:
- Local INPUT folder (default)
- Custom local folder (user selected)
- Google Drive folder
"""

from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

from doc_validator.config import INPUT_FOLDER
from doc_validator.core.drive_io import (
    authenticate_drive_api,
    get_all_excel_files_from_folder,
)


@dataclass
class FileInfo:
    """Information about an Excel file from any source."""
    name: str
    source_type: str  # "local" or "drive"
    # For local files
    local_path: Optional[str] = None
    # For Drive files
    file_id: Optional[str] = None
    mime_type: Optional[str] = None


type_of_input_file = ["*.xlsx", "*.xls", "*.XLSX", "*.XLS"]


def get_local_excel_files(folder_path: str) -> List[FileInfo]:
    """
    Get all Excel files from a local folder.

    Args:
        folder_path: Path to local folder

    Returns:
        List of FileInfo objects for local Excel files
    """
    folder = Path(folder_path)

    if not folder.exists() or not folder.is_dir():
        return []

    excel_files = []

    # Find all Excel files (case-insensitive)
    seen = set()
    for pattern in type_of_input_file:
        for file_path in folder.glob(pattern):
            if not file_path.is_file():
                continue
            if file_path.resolve() in seen:
                continue
            seen.add(file_path.resolve())
            excel_files.append(
                FileInfo(
                    name=file_path.name,
                    source_type="local",
                    local_path=str(file_path),
                )
            )

    # Sort by name
    excel_files.sort(key=lambda x: x.name.lower())

    return excel_files


def get_drive_excel_files(api_key: str, folder_id: str) -> List[FileInfo]:
    """
    Get all Excel files from Google Drive folder.

    Args:
        api_key: Google Drive API key
        folder_id: Google Drive folder ID

    Returns:
        List of FileInfo objects for Drive Excel files
    """
    try:
        drive_service = authenticate_drive_api(api_key)
        drive_files = get_all_excel_files_from_folder(drive_service, folder_id)

        return [
            FileInfo(
                name=f["name"],
                source_type="drive",
                file_id=f["id"],
                mime_type=f.get("mimeType", ""),
            )
            for f in drive_files
        ]
    except Exception as e:
        print(f"Error loading Drive files: {e}")
        return []


def get_default_input_folder() -> str:
    """Get the default INPUT folder path."""
    return INPUT_FOLDER
