# doc_validator/tools/process_local_batch.py
"""
Process multiple Excel files from a local folder.
Alternative to Google Drive for batch processing local files.

Usage:
    python -m doc_validator.tools.process_local_batch <folder_path>

Example:
    python -m doc_validator.tools.process_local_batch "C:/Users/YourName/Documents/ExcelFiles"
"""

import sys
import os
from pathlib import Path

from doc_validator.core.excel_pipeline import process_excel


def get_excel_files(folder_path):
    """
    Get all Excel files from a local folder.

    Args:
        folder_path: Path to folder containing Excel files

    Returns:
        list: List of Excel file paths
    """
    folder = Path(folder_path)

    if not folder.exists():
        print(f"❌ Error: Folder does not exist: {folder_path}")
        return []

    if not folder.is_dir():
        print(f"❌ Error: Not a directory: {folder_path}")
        return []

    # Find all Excel files (case-insensitive)
    excel_files = []
    excel_files.extend(folder.glob("*.xlsx"))
    excel_files.extend(folder.glob("*.xls"))
    excel_files.extend(folder.glob("*.XLSX"))
    excel_files.extend(folder.glob("*.XLS"))

    # Convert to strings and sort
    excel_files = sorted(str(f) for f in excel_files)

    return excel_files


def process_local_batch(folder_path):
    """
    Process all Excel files in a local folder.

    Args:
        folder_path: Path to folder containing Excel files

    Returns:
        list: List of processed file info dicts:
              [{'original': <input>, 'output': <output_or_None>}, ...]
    """
    print("=" * 60)
    print("LOCAL BATCH PROCESSOR")
    print("=" * 60)
    print(f"\n📁 Folder: {folder_path}\n")

    # Get all Excel files
    excel_files = get_excel_files(folder_path)

    if not excel_files:
        print("❌ No Excel files found in folder.")
        return []

    print(f"📊 Found {len(excel_files)} Excel file(s):")
    for i, file in enumerate(excel_files, 1):
        print(f"   {i}. {os.path.basename(file)}")

    # Process each file
    print("\n" + "=" * 60)
    print(f"PROCESSING {len(excel_files)} FILE(S)")
    print("=" * 60)

    processed_files = []
    failed_files = []

    for i, file_path in enumerate(excel_files, 1):
        print(f"\n{'=' * 60}")
        print(f"FILE {i}/{len(excel_files)}: {os.path.basename(file_path)}")
        print(f"{'=' * 60}")

        try:
            output_path = process_excel(file_path)

            if output_path:
                processed_files.append(
                    {
                        "original": file_path,
                        "output": output_path,
                    }
                )
                print(f"\n✅ Successfully processed: {os.path.basename(file_path)}")
            else:
                failed_files.append(file_path)
                print(f"\n❌ Failed to process: {os.path.basename(file_path)}")

        except Exception as e:  # pragma: no cover
            failed_files.append(file_path)
            print(f"\n❌ Error processing {os.path.basename(file_path)}: {str(e)}")
            import traceback

            traceback.print_exc()

    # Final summary
    print("\n" + "=" * 60)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   Total files: {len(excel_files)}")
    print(f"   ✅ Successful: {len(processed_files)}")
    print(f"   ❌ Failed: {len(failed_files)}")

    if processed_files:
        print(f"\n✅ Successfully processed files:")
        for i, file in enumerate(processed_files, 1):
            print(f"   {i}. {os.path.basename(file['original'])}")
            print(f"      → {file['output']}")

    if failed_files:
        print(f"\n❌ Failed files:")
        for i, file in enumerate(failed_files, 1):
            print(f"   {i}. {os.path.basename(file)}")

    print("\n" + "=" * 60)

    return processed_files


def main():
    """Main entry point for local batch processing."""
    if len(sys.argv) < 2:
        print("Usage: python -m doc_validator.tools.process_local_batch <folder_path>")
        print("\nExample:")
        print(
            '  python -m doc_validator.tools.process_local_batch "C:/Users/YourName/Documents/ExcelFiles"'
        )
        print('  python -m doc_validator.tools.process_local_batch "./DATA/raw_files"')
        sys.exit(1)

    folder_path = sys.argv[1]
    processed_files = process_local_batch(folder_path)

    if processed_files:
        print(f"\n✅ Success! Processed {len(processed_files)} file(s)")
    else:
        print("\n❌ No files were processed successfully")


if __name__ == "__main__":
    main()
