# doc_validator/core/pipeline.py
"""
High-level processing pipeline that connects:
- Google Drive I/O
- Excel validation pipeline

This module is the "brain" that both CLI and GUI code will call.
"""

from typing import Callable, List, Dict, Any, Optional
from datetime import date

from doc_validator.core.drive_io import (
    authenticate_drive_api,
    download_all_excel_files,
    read_credentials_file,
)
from doc_validator.core.excel_pipeline import process_excel


Logger = Callable[[str], None]


def _default_logger(message: str) -> None:
    """Fallback logger: just print to stdout."""
    print(message)


def process_work_package(
    api_key: str,
    folder_id: str,
    *,
    filter_start_date: Optional[date] = None,
    filter_end_date: Optional[date] = None,
    enable_action_step_control: bool = True,
    logger: Optional[Logger] = None,
) -> List[Dict[str, Any]]:
    """
    High-level pipeline with optional date filtering.
    - Authenticates to Google Drive
    - Downloads **all Excel files** in the given folder
    - Runs the Excel validation pipeline on each (with optional date filter)
    - Optionally runs Action Step Control (ASC) and adds its sheet
      to the output workbook.
    - Returns a list of results (one per file)

    Args:
        api_key: Google Drive API key (GG_API_KEY)
        folder_id: Google Drive folder ID (GG_FOLDER_ID)
        filter_start_date: Optional start date for filtering
        filter_end_date: Optional end date for filtering
        enable_action_step_control: If True, generate ASC sheet for each file
        logger: Optional logging function (e.g., for GUI). Defaults to print.

    Returns:
        List of dicts, one per processed file:
        [
            {
                "source_name": <original filename>,
                "source_id": <drive file id>,
                "local_path": <downloaded local path>,
                "output_file": <validated Excel file path or None>,
            },
            ...
        ]
    """
    log = logger or _default_logger

    if not api_key:
        raise ValueError("API key is required")
    if not folder_id:
        raise ValueError("Folder ID is required")

    log("=== STARTING WORK PACKAGE PROCESSING ===")

    # 1) Authenticate
    log("Authenticating with Google Drive API...")
    drive_service = authenticate_drive_api(api_key)
    log("✓ Authentication successful")

    # 2) Download all Excel files from folder
    log("Listing and downloading Excel files from folder...")
    downloaded_files = download_all_excel_files(drive_service, folder_id)

    if not downloaded_files:
        log("No Excel files were downloaded. Nothing to process.")
        log("=== PROCESSING FINISHED (NO FILES) ===")
        return []

    log(f"✓ Downloaded {len(downloaded_files)} file(s).")

    # 3) Process each downloaded Excel file
    results: List[Dict[str, Any]] = []

    for idx, file_info in enumerate(downloaded_files, start=1):
        src_name = file_info.get("name")
        src_id = file_info.get("id")
        local_path = file_info.get("path")

        log("")
        log(f"[{idx}/{len(downloaded_files)}] Processing file: {src_name}")
        log(f"    Local path: {local_path}")

        # Process with optional date filter + ASC flag
        output_file = process_excel(
            local_path,
            filter_start_date=filter_start_date,
            filter_end_date=filter_end_date,
            enable_action_step_control=enable_action_step_control,
        )

        if output_file:
            log(f"    ✓ Output file created: {output_file}")
        else:
            log("    ✗ Processing failed for this file")

        results.append(
            {
                "source_name": src_name,
                "source_id": src_id,
                "local_path": local_path,
                "output_file": output_file,
            }
        )

    log("")
    log("=== ALL FILES PROCESSED ===")
    return results


def process_from_credentials_file(
    credentials_path: str = "link.txt",
    *,
    filter_start_date: Optional[date] = None,
    filter_end_date: Optional[date] = None,
    enable_action_step_control: bool = True,
    logger: Optional[Logger] = None,
) -> List[Dict[str, Any]]:
    """
    Convenience wrapper: read GG_API_KEY and GG_FOLDER_ID from a credentials file
    (like your existing link.txt), then run `process_work_package`.

    Args:
        credentials_path: Path to credentials file (default: 'link.txt')
        filter_start_date: Optional start date for filtering
        filter_end_date: Optional end date for filtering
        enable_action_step_control: If True, generate ASC sheet for each file
        logger: Optional logger (for CLI/GUI)

    Returns:
        Same as process_work_package(): list of per-file result dicts.
    """
    log = logger or _default_logger

    log(f"Reading credentials from: {credentials_path}")
    api_key, folder_id = read_credentials_file(credentials_path)

    if not api_key or not folder_id:
        raise ValueError(
            f"Invalid credentials in {credentials_path}: "
            f"GG_API_KEY or GG_FOLDER_ID missing."
        )

    return process_work_package(
        api_key,
        folder_id,
        filter_start_date=filter_start_date,
        filter_end_date=filter_end_date,
        enable_action_step_control=enable_action_step_control,
        logger=logger,
    )
