"""
excel_utils.py - SIMPLIFIED VERSION with SEQ filtering
Updated to work with 3-state validation (removed "No reference type")
Now automatically marks SEQ 1.xx, 2.xx, 3.xx, 10.xx as Valid

Statistics now track:
- Valid
- Missing reference
- Missing reference type
- Missing revision
- N/A

UPDATED: Logbook system
- Instead of per-run .txt logs, we now append to a monthly Excel logbook:
  DATA/log/logbook_YYYY_MM.xlsx
"""

import os
import re
import pandas as pd
from datetime import datetime
from doc_validator.validation.engine import check_ref_keywords
from doc_validator.config import DATA_FOLDER, LOG_FOLDER, INVALID_CHARACTERS


def sanitize_folder_name(wp_value):
    """Clean folder name by removing invalid characters."""
    if isinstance(wp_value, str) and wp_value.strip():
        cleaned_wp_value = re.sub(INVALID_CHARACTERS, '_', wp_value)
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
        os.path.basename(output_file).replace('.xlsx', '.txt')
    )

    with open(log_filename, 'w', encoding='utf-8') as log_file:
        # Header
        log_file.write("=" * 60 + "\n")
        log_file.write("AIRCRAFT MAINTENANCE VALIDATION LOG\n")
        log_file.write("=" * 60 + "\n\n")

        # Metadata
        log_file.write(f"Output file: {output_file}\n")
        log_file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"Work Package: {wp_value}\n")
        if processing_time:
            log_file.write(f"Processing Time: {processing_time:.2f} seconds\n")
        log_file.write("\n")

        # Statistics
        log_file.write("VALIDATION STATISTICS\n")
        log_file.write("-" * 60 + "\n")
        log_file.write(f"Total rows processed: {counts.get('out_rows', 0)}\n")
        log_file.write(f"Original rows: {counts.get('orig_rows', 0)}\n")

        if counts.get('orig_rows') != counts.get('out_rows'):
            log_file.write(f"⚠️ WARNING: Row count mismatch detected!\n")

        log_file.write("\n")

        # SEQ auto-valid count
        if counts.get('seq_auto_valid', 0) > 0:
            log_file.write(f"SEQ Auto-Valid (1.xx, 2.xx, 3.xx, 10.xx): {counts.get('seq_auto_valid', 0)}\n")
            log_file.write("\n")

        # Validation results (SIMPLIFIED - only 3 categories)
        log_file.write("VALIDATION RESULTS\n")
        log_file.write("-" * 60 + "\n")
        log_file.write(f"✓ Valid: {counts.get('Valid', 0)}\n")
        log_file.write(f"• N/A: {counts.get('N/A', 0)}\n")
        log_file.write(f"✗ Missing reference: {counts.get('Missing reference', 0)}\n")
        log_file.write(f"✗ Missing reference type: {counts.get('Missing reference type', 0)}\n")
        log_file.write(f"✗ Missing revision: {counts.get('Missing revision', 0)}\n")

        # Total errors (simplified calculation)
        total_errors = (
            counts.get('Missing reference', 0) +
            counts.get('Missing reference type', 0) +
            counts.get('Missing revision', 0)
        )

        log_file.write("\n")
        log_file.write(f"Total rows with errors: {total_errors}\n")

        # Error rate
        if counts.get('out_rows', 0) > 0:
            error_rate = (total_errors / counts.get('out_rows')) * 100
            log_file.write(f"Error rate: {error_rate:.2f}%\n")

        log_file.write("\n" + "=" * 60 + "\n")

    print(f"✓ Legacy txt log file created: {log_filename}")


def append_to_logbook(wp_value, counts, processing_time=None):
    """
    Append one run to a monthly Excel logbook.

    - File name format: logbook_YYYY_MM.xlsx
    - Stored under: DATA/LOG_FOLDER (e.g. DATA/log/logbook_2025_11.xlsx)

    Columns include (after cleanup):
    - Order, DateTime, WP
    - Orig rows, Out rows, Valid, N/A
    - Missing reference, Missing reference type, Missing revision
    - Seq auto-valid, Row mismatch flag
    - Total errors, Error rate (%), Processing time (s)
    """
    now = datetime.now()
    month_str = now.strftime("%Y_%m")  # e.g., 2025_11

    logbook_folder = os.path.join(DATA_FOLDER, LOG_FOLDER)
    os.makedirs(logbook_folder, exist_ok=True)

    logbook_path = os.path.join(logbook_folder, f"logbook_{month_str}.xlsx")

    # Compute totals
    missing_ref = counts.get('Missing reference', 0)
    missing_ref_type = counts.get('Missing reference type', 0)
    missing_rev = counts.get('Missing revision', 0)
    seq_auto_valid = counts.get('seq_auto_valid', 0)

    total_errors = missing_ref + missing_ref_type + missing_rev
    out_rows = counts.get('out_rows', 0)
    error_rate = (total_errors / out_rows * 100) if out_rows > 0 else 0.0

    row_mismatch = counts.get('orig_rows', 0) != counts.get('out_rows', 0)

    # Row data AFTER removing Date, Time, Output file
    row = {
        "Order": None,
        "DateTime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "WP": wp_value,
        "Orig rows": counts.get('orig_rows', 0),
        "Out rows": out_rows,
        "Valid": counts.get('Valid', 0),
        "N/A": counts.get('N/A', 0),
        "Missing reference": missing_ref,
        "Missing reference type": missing_ref_type,
        "Missing revision": missing_rev,
        "SEQ auto-valid": seq_auto_valid,
        "Row mismatch": row_mismatch,
        "Total errors": total_errors,
        "Error rate (%)": round(error_rate, 2),
        "Processing time (s)": round(processing_time, 2) if processing_time is not None else None,
    }

    # Append or create
    if os.path.exists(logbook_path):
        existing_df = pd.read_excel(logbook_path)
        row["Order"] = len(existing_df) + 1
        df = pd.concat([existing_df, pd.DataFrame([row])], ignore_index=True)
    else:
        row["Order"] = 1
        df = pd.DataFrame([row])

    df.to_excel(logbook_path, index=False)
    print(f"✓ Logbook updated: {logbook_path}")


def validate_dataframe(df):
    """
    Validate DataFrame before processing.
    Returns tuple: (is_valid, error_message)
    """
    if df is None or df.empty:
        return False, "DataFrame is empty"

    if df.shape[0] == 0:
        return False, "No rows to process"

    # Check if 'wo_text_action.text' column exists or can be found
    if 'wo_text_action.text' not in df.columns:
        candidates = [c for c in df.columns if 'wo_text_action.text' in str(c).lower()]
        if not candidates:
            return False, "No 'wo_text_action.text' column found in Excel file"

    return True, None


def extract_wp_value(df):
    """
    Safely extract work package value from DataFrame.
    Now looks for 'WP' column (uppercase) instead of 'wp'.
    """
    # Try to find WP column (case-insensitive)
    wp_col = None
    for col in df.columns:
        if col.upper() == 'WP':
            wp_col = col
            break

    if wp_col is None:
        print("   ⚠️ No 'WP' column found in Excel file")
        return "No_wp_found"

    # Drop NaN values and check if any valid values remain
    wp_series = df[wp_col].dropna()

    if wp_series.empty:
        return "No_wp_found"

    # Get first non-empty value
    wp_value = str(wp_series.iloc[0]).strip()

    if not wp_value or wp_value.upper() in ['N/A', 'NA', 'NONE', '']:
        return "No_wp_found"

    return wp_value


def process_excel(file_path):
    """
    Process Excel file with simplified 3-state validation.
    NEW: Automatically marks SEQ 1.xx, 2.xx, 3.xx, 10.xx as Valid

    Returns only:
    - Valid
    - Missing reference
    - Missing reference type
    - Missing revision
    - N/A
    """
    print("\n" + "="*60)
    print("PROCESSING EXCEL FILE")
    print("="*60)

    start_time = datetime.now()

    try:
        # ========== STEP 1: Read Excel File ==========
        print(f"\n1. Reading file: {os.path.basename(file_path)}")

        # CRITICAL: Read with minimal processing to avoid data loss
        df = pd.read_excel(
            file_path,
            engine='openpyxl',
            header=0,
            sheet_name=0,
            keep_default_na=False,  # Keep "N/A" as literal wo_text_action.text
            dtype=str,              # Read everything as string
            na_filter=False         # IMPORTANT: Don't filter NA values at all
        )

        print(f"   ✓ Read {df.shape[0]} rows, {df.shape[1]} columns")

        # DIAGNOSTIC: Check for any empty rows that might get dropped
        empty_rows = df[df.apply(lambda x: x.str.strip().eq('').all(), axis=1)]
        if not empty_rows.empty:
            print(f"   ⚠️ Found {len(empty_rows)} completely empty rows")

        # ========== STEP 2: Validate DataFrame ==========
        is_valid, error_msg = validate_dataframe(df)
        if not is_valid:
            print(f"   ✗ Validation error: {error_msg}")
            return None

        orig_rows = df.shape[0]

        # In excel_utils.py, update the process_excel function
        # Find the section around line 200-250 where validation is applied

        # BEFORE (old code):
        # df['Reason'] = df.apply(
        #     lambda row: check_ref_keywords(row['wo_text_action.text'], row['SEQ']),
        #     axis=1
        # )

        # AFTER (new code with header):

        # ========== STEP 3: Prepare columns (UPDATED) ==========
        print("\n2. Preparing data for validation...")

        # Prepare wo_text_action.text column (existing code)
        if 'wo_text_action.text' not in df.columns:
            candidates = [c for c in df.columns if 'wo_text_action.text' in str(c).lower()]
            if candidates:
                df = df.rename(columns={candidates[0]: 'wo_text_action.text'})
                print(f"   ✓ Renamed '{candidates[0]}' to 'wo_text_action.text'")
            else:
                df['wo_text_action.text'] = "N/A"
                print("   ⚠️ No wo_text_action.text column found, created empty column")

        df['wo_text_action.text'] = df['wo_text_action.text'].fillna("N/A").astype(str)

        # Prepare SEQ column (existing code)
        if 'SEQ' not in df.columns:
            seq_candidates = [c for c in df.columns if c.upper() == 'SEQ']
            if seq_candidates:
                df = df.rename(columns={seq_candidates[0]: 'SEQ'})
                print(f"   ✓ Found SEQ column: '{seq_candidates[0]}'")
            else:
                df['SEQ'] = None
                print("   ⚠️ No SEQ column found, validation will proceed normally")

        df['SEQ'] = df['SEQ'].fillna("")

        # NEW: Prepare wo_text_action.header column
        if 'wo_text_action.header' not in df.columns:
            header_candidates = [c for c in df.columns if 'wo_text_action.header' in str(c).lower()]
            if header_candidates:
                df = df.rename(columns={header_candidates[0]: 'wo_text_action.header'})
                print(f"   ✓ Found header column: '{header_candidates[0]}'")
            else:
                df['wo_text_action.header'] = None
                print("   ⚠️ No wo_text_action.header column found, validation will proceed normally")

        df['wo_text_action.header'] = df['wo_text_action.header'].fillna("")

        # ========== STEP 4: Apply Validation with SEQ and HEADER (UPDATED) ==========
        print("\n3. Validating documentation references...")
        print("   ℹ️ SEQ 1.xx, 2.xx, 3.xx, 10.xx will be marked as Valid automatically")
        print("   ℹ️ Headers with CLOSE UP, JOB SET UP, OPEN/CLOSE ACCESS, GENERAL will be marked as Valid")

        # Apply validation with both SEQ and HEADER parameters
        df['Reason'] = df.apply(
            lambda row: check_ref_keywords(
                row['wo_text_action.text'],
                row['SEQ'],
                row['wo_text_action.header']  # NEW: Pass header to validation
            ),
            axis=1
        )

        print("   ✓ Validation complete")

        # ========== STEP 5: Calculate Statistics (add header count) ==========
        counts = {
            'orig_rows': orig_rows,
            'out_rows': int(df.shape[0]),
            'Missing reference': int((df['Reason'] == 'Missing reference').sum()),
            'Missing reference type': int((df['Reason'] == 'Missing reference type').sum()),
            'Missing revision': int((df['Reason'] == 'Missing revision').sum()),
            'Valid': int((df['Reason'] == 'Valid').sum()),
            'N/A': int((df['Reason'] == 'N/A').sum())
        }
        # After existing counts, add:

        # Count header auto-valid rows (NEW)
        from validators import contains_header_skip_keyword
        counts['header_auto_valid'] = int(
            df['wo_text_action.header'].apply(contains_header_skip_keyword).sum()
        )

        # Then in the display statistics section, add:
        if counts['header_auto_valid'] > 0:
            print(f"      (includes {counts['header_auto_valid']} header auto-valid rows)")

        print("   ✓ Validation complete")


        # Count SEQ auto-valid rows
        from validators import is_seq_auto_valid
        counts['seq_auto_valid'] = int(df['SEQ'].apply(is_seq_auto_valid).sum())

        # ========== STEP 6: CRITICAL - Check for Row Count Mismatch ==========
        if counts['orig_rows'] != counts['out_rows']:
            print(f"\n   🔴 CRITICAL: Row count mismatch detected!")
            print(f"      Original rows: {counts['orig_rows']}")
            print(f"      Output rows: {counts['out_rows']}")
            print(f"      LOST ROWS: {counts['orig_rows'] - counts['out_rows']}")

            # Save BOTH input and output for comparison
            debug_folder = os.path.join(os.path.dirname(file_path), "DEBUG")
            os.makedirs(debug_folder, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Re-read original to save it
            df_original = pd.read_excel(
                file_path,
                engine='openpyxl',
                header=0,
                sheet_name=0,
                keep_default_na=False,
                dtype=str,
                na_filter=False
            )

            debug_input = os.path.join(debug_folder, f"input_original_{timestamp}.csv")
            debug_output = os.path.join(debug_folder, f"output_processed_{timestamp}.csv")

            df_original.to_csv(debug_input, index=False, encoding='utf-8')
            df.to_csv(debug_output, index=False, encoding='utf-8')

            print(f"      Debug files saved:")
            print(f"        Input:  {debug_input}")
            print(f"        Output: {debug_output}")
            print(f"      Compare these files to find missing rows!")

        # Verify row counts match
        total_counted = sum([
            counts['Valid'],
            counts['N/A'],
            counts['Missing reference'],
            counts['Missing reference type'],
            counts['Missing revision']
        ])

        if total_counted != counts['out_rows']:
            print(f"\n   ⚠️ WARNING: Count verification failed!")
            print(f"      Sum of categories: {total_counted}")
            print(f"      Total rows: {counts['out_rows']}")
            print(f"      This suggests an uncategorized reason exists!")

        # ========== STEP 7: Display Statistics (SIMPLIFIED) ==========
        print("\n4. Validation Statistics:")
        print(f"   ✓ Valid: {counts['Valid']}")

        if counts['seq_auto_valid'] > 0:
            print(f"      (includes {counts['seq_auto_valid']} SEQ auto-valid rows)")

        print(f"   • N/A: {counts['N/A']}")
        print(f"   ✗ Missing reference: {counts['Missing reference']}")
        print(f"   ✗ Missing reference type: {counts['Missing reference type']}")
        print(f"   ✗ Missing revision: {counts['Missing revision']}")

        total_errors = (
            counts['Missing reference'] +
            counts['Missing reference type'] +
            counts['Missing revision']
        )
        print(f"\n   Total errors: {total_errors}")

        if counts['out_rows'] > 0:
            error_rate = (total_errors / counts['out_rows']) * 100
            print(f"   Error rate: {error_rate:.1f}%")

        # ========== STEP 8: Prepare Output ==========
        print("\n5. Preparing output file...")

        wp_value = extract_wp_value(df)
        cleaned_folder_name = sanitize_folder_name(wp_value).replace(' ', '_')

        output_folder = os.path.join(DATA_FOLDER, cleaned_folder_name)
        os.makedirs(output_folder, exist_ok=True)

        current_time = datetime.now().strftime("%I%p%M_%d_%m_%y").lower()
        output_file = os.path.join(
            output_folder,
            f"WP_{cleaned_folder_name}_{current_time}.xlsx"
        )

        # ========== STEP 9: Write Excel File ==========
        print(f"   Writing to: {os.path.basename(output_file)}")

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, header=True)
            workbook = writer.book
            sheet = workbook.active

            # IMPORTANT: Add hidden rows with all possible Reason values
            # This ensures ALL statuses appear in filter dropdown even if count = 0
            possible_reasons = [
                'Valid',
                'Missing reference',
                'Missing reference type',
                'Missing revision',
                'N/A'
            ]

            # Find the Reason column index (1-based for Excel)
            reason_col_idx = None
            for idx, col in enumerate(df.columns, start=1):
                if col == 'Reason':
                    reason_col_idx = idx
                    break

            if reason_col_idx:
                # Get last row with actual data
                last_data_row = sheet.max_row

                # Add hidden rows at the end for each possible reason
                for i, reason in enumerate(possible_reasons, start=1):
                    hidden_row = last_data_row + i

                    # Write the reason value in Reason column only
                    sheet.cell(row=hidden_row, column=reason_col_idx, value=reason)

                    # Hide the row so it doesn't show in normal view
                    sheet.row_dimensions[hidden_row].hidden = True

                print(f"   ✓ Added {len(possible_reasons)} hidden reference rows for complete filter dropdown")

                # Apply auto-filter to include hidden rows
                # This makes all possible values appear in the filter dropdown
                last_col_letter = sheet.cell(row=1, column=sheet.max_column).column_letter
                sheet.auto_filter.ref = f"A1:{last_col_letter}{sheet.max_row}"
            else:
                # Fallback if Reason column not found
                sheet.auto_filter.ref = sheet.dimensions
                print("   ⚠️ Reason column not found, using standard filter")

            workbook.save(output_file)

        print(f"   ✓ File saved")

        # ========== STEP 10: Create Log Book Entry (Excel) ==========
        processing_time = (datetime.now() - start_time).total_seconds()
        append_to_logbook(cleaned_folder_name, counts, processing_time)

        # If you still want txt logs as backup, uncomment this:
        # create_log_file(cleaned_folder_name, output_file, counts, processing_time)

        # ========== FINAL SUMMARY ==========
        print("\n" + "="*60)
        print("✓ PROCESSING COMPLETE")
        print("="*60)
        print(f"Output: {os.path.abspath(output_file)}")
        print(f"Processing time: {processing_time:.2f} seconds")
        print("="*60 + "\n")

        return output_file

    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
