# doc_validator/core/excel_io.py

import os
import re
from datetime import datetime

import pandas as pd

from doc_validator.config import DATA_FOLDER, LOG_FOLDER, INVALID_CHARACTERS


def sanitize_folder_name(wp_value: str) -> str:
    """Clean folder name by removing invalid characters."""
    if isinstance(wp_value, str) and wp_value.strip():
        cleaned_wp_value = re.sub(INVALID_CHARACTERS, "_", wp_value)
        return cleaned_wp_value
    return "No_wp_found"


def create_log_file(wp_value, output_file, counts, processing_time=None):
    """
    (LEGACY) Create a detailed log file with validation summary as .txt.
    Kept for backward compatibility but no longer used by default.
    """
    log_folder = os.path.join(DATA_FOLDER, wp_value, LOG_FOLDER)
    os.makedirs(log_folder, exist_ok=True)

    log_filename = os.path.join(
        log_folder,
        os.path.basename(output_file).replace(".xlsx", ".txt"),
    )

    from datetime import datetime as _dt

    with open(log_filename, "w", encoding="utf-8") as log_file:
        # Header
        log_file.write("=" * 60 + "\n")
        log_file.write("AIRCRAFT MAINTENANCE VALIDATION LOG\n")
        log_file.write("=" * 60 + "\n\n")

        # Metadata
        log_file.write(f"Output file: {output_file}\n")
        log_file.write(f"Generated: {_dt.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"Work Package: {wp_value}\n")
        if processing_time:
            log_file.write(f"Processing Time: {processing_time:.2f} seconds\n")
        log_file.write("\n")

        # Statistics
        log_file.write("VALIDATION STATISTICS\n")
        log_file.write("-" * 60 + "\n")
        log_file.write(f"Total rows processed: {counts.get('out_rows', 0)}\n")
        log_file.write(f"Original rows: {counts.get('orig_rows', 0)}\n")

        if counts.get("orig_rows") != counts.get("out_rows"):
            log_file.write("⚠️ WARNING: Row count mismatch detected!\n")

        log_file.write("\n")

        # SEQ auto-valid count
        if counts.get("seq_auto_valid", 0) > 0:
            log_file.write(
                f"SEQ Auto-Valid (1.xx, 2.xx, 3.xx, 10.xx): "
                f"{counts.get('seq_auto_valid', 0)}\n\n"
            )

        # Validation results
        log_file.write("VALIDATION RESULTS\n")
        log_file.write("-" * 60 + "\n")
        log_file.write(f"✓ Valid: {counts.get('Valid', 0)}\n")
        log_file.write(f"• N/A: {counts.get('N/A', 0)}\n")
        log_file.write(f"✗ Missing reference: {counts.get('Missing reference', 0)}\n")
        log_file.write(
            f"✗ Missing reference type: {counts.get('Missing reference type', 0)}\n"
        )
        log_file.write(f"✗ Missing revision: {counts.get('Missing revision', 0)}\n")

        total_errors = (
            counts.get("Missing reference", 0)
            + counts.get("Missing reference type", 0)
            + counts.get("Missing revision", 0)
        )

        log_file.write("\n")
        log_file.write(f"Total rows with errors: {total_errors}\n")

        if counts.get("out_rows", 0) > 0:
            error_rate = (total_errors / counts.get("out_rows")) * 100
            log_file.write(f"Error rate: {error_rate:.2f}%\n")

        log_file.write("\n" + "=" * 60 + "\n")

    print(f"✓ Legacy txt log file created: {log_filename}")


def append_to_logbook(wp_value, counts, processing_time=None):
    """
    Append one run to a monthly Excel logbook.

    - File name format: logbook_YYYY_MM.xlsx
    - Stored under: DATA/LOG_FOLDER (e.g. DATA/log/logbook_2025_11.xlsx)
    """
    now = datetime.now()
    month_str = now.strftime("%Y_%m")  # e.g., 2025_11

    logbook_folder = os.path.join(DATA_FOLDER, LOG_FOLDER)
    os.makedirs(logbook_folder, exist_ok=True)

    logbook_path = os.path.join(logbook_folder, f"logbook_{month_str}.xlsx")

    # Compute totals
    missing_ref = counts.get("Missing reference", 0)
    missing_ref_type = counts.get("Missing reference type", 0)
    missing_rev = counts.get("Missing revision", 0)
    seq_auto_valid = counts.get("seq_auto_valid", 0)

    total_errors = missing_ref + missing_ref_type + missing_rev
    out_rows = counts.get("out_rows", 0)
    error_rate = (total_errors / out_rows * 100) if out_rows > 0 else 0.0

    row_mismatch = counts.get("orig_rows", 0) != counts.get("out_rows", 0)

    row = {
        "Order": None,
        "DateTime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "WP": wp_value,
        "Orig rows": counts.get("orig_rows", 0),
        "Out rows": out_rows,
        "Valid": counts.get("Valid", 0),
        "N/A": counts.get("N/A", 0),
        "Missing reference": missing_ref,
        "Missing reference type": missing_ref_type,
        "Missing revision": missing_rev,
        "SEQ auto-valid": seq_auto_valid,
        "Row mismatch": row_mismatch,
        "Total errors": total_errors,
        "Error rate (%)": round(error_rate, 2),
        "Processing time (s)": round(processing_time, 2)
        if processing_time is not None
        else None,
    }

    if os.path.exists(logbook_path):
        existing_df = pd.read_excel(logbook_path)
        row["Order"] = len(existing_df) + 1
        df = pd.concat([existing_df, pd.DataFrame([row])], ignore_index=True)
    else:
        row["Order"] = 1
        df = pd.DataFrame([row])

    df.to_excel(logbook_path, index=False)
    print(f"✓ Logbook updated: {logbook_path}")


def read_input_excel(file_path: str) -> pd.DataFrame:
    """
    Read the input Excel file with the strict settings used in the original code,
    to avoid data loss.
    """
    df = pd.read_excel(
        file_path,
        engine="openpyxl",
        header=0,
        sheet_name=0,
        keep_default_na=False,  # Keep "N/A" as literal
        dtype=str,  # Read everything as string
        na_filter=False,  # Do not convert to NaN
    )
    return df


def reread_original_for_debug(file_path: str) -> pd.DataFrame:
    """
    Re-read the original Excel for debug comparison.
    Mirrors read_input_excel().
    """
    return read_input_excel(file_path)


def save_debug_input_output(file_path: str, df_processed: pd.DataFrame) -> None:
    """
    Save input and output CSVs to a DEBUG folder for row loss diagnosis.
    """
    debug_folder = os.path.join(os.path.dirname(file_path), "DEBUG")
    os.makedirs(debug_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    df_original = reread_original_for_debug(file_path)

    debug_input = os.path.join(debug_folder, f"input_original_{timestamp}.csv")
    debug_output = os.path.join(debug_folder, f"output_processed_{timestamp}.csv")

    df_original.to_csv(debug_input, index=False, encoding="utf-8")
    df_processed.to_csv(debug_output, index=False, encoding="utf-8")

    print("      Debug files saved:")
    print(f"        Input:  {debug_input}")
    print(f"        Output: {debug_output}")
    print("      Compare these files to find missing rows!")


def build_output_path(wp_value: str) -> tuple[str, str]:
    """
    Build output folder and full Excel file path for a given WP.
    Returns (cleaned_folder_name, output_file).
    """
    cleaned_folder_name = sanitize_folder_name(wp_value).replace(" ", "_")
    output_folder = os.path.join(DATA_FOLDER, cleaned_folder_name)
    os.makedirs(output_folder, exist_ok=True)

    current_time = datetime.now().strftime("%I%p%M_%d_%m_%y").lower()
    output_file = os.path.join(
        output_folder,
        f"WP_{cleaned_folder_name}_{current_time}.xlsx",
    )
    return cleaned_folder_name, output_file


def write_output_excel(df: pd.DataFrame, output_file: str) -> None:
    """
    Write the processed DataFrame to Excel.

    - No extra rows are added.
    - Auto-filter is applied over the actual data range only.
    """
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, header=True)

        workbook = writer.book
        sheet = workbook.active

        # Apply auto filter to the data range
        last_row = sheet.max_row
        last_col_letter = sheet.cell(row=1, column=sheet.max_column).column_letter
        sheet.auto_filter.ref = f"A1:{last_col_letter}{last_row}"

    print(f"   ✓ File saved: {os.path.basename(output_file)}")
