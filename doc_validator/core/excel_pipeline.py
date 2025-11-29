# doc_validator/core/excel_pipeline.py

from datetime import datetime, date

import pandas as pd

from doc_validator.validation.engine import check_ref_keywords
from doc_validator.config import (
    ACTION_STEP_CONTROL_ENABLED_DEFAULT,
    ACTION_STEP_SHEET_NAME,
    ACTION_STEP_SUMMARY_ENABLED_DEFAULT,
    ACTION_STEP_SUMMARY_SHEET_NAME,
)
from doc_validator.tools.action_step_control import compute_action_step_control_df
from doc_validator.tools.action_step_control import compute_action_step_control_df
from doc_validator.validation.helpers import (
    contains_header_skip_keyword,
    is_seq_auto_valid,
)
from .excel_io import (
    read_input_excel,
    save_debug_input_output,
    append_to_logbook,
    build_output_path,
    write_output_excel,
    sanitize_folder_name,
)


def run_action_step_control_hook(
    df: pd.DataFrame,
    wp_value: str,
    source_file: str,
    enable_action_step_control: bool = ACTION_STEP_CONTROL_ENABLED_DEFAULT,
) -> dict[str, pd.DataFrame] | None:
    """
    Hook to compute extra sheets for Action Step Control.

    Returns:
        dict[sheet_name, DataFrame] or None if ASC is disabled or fails.
    """
    if not enable_action_step_control:
        return None

    try:
        asc_df, summary_df, asc_wp = compute_action_step_control_df(df)

        extra_sheets: dict[str, pd.DataFrame] = {
            ACTION_STEP_SHEET_NAME: asc_df,
        }

        if ACTION_STEP_SUMMARY_ENABLED_DEFAULT and not summary_df.empty:
            extra_sheets[ACTION_STEP_SUMMARY_SHEET_NAME] = summary_df

        print(
            f"[ASC] Added sheets: {', '.join(extra_sheets.keys())} "
            f"for WP={asc_wp or wp_value}"
        )

        return extra_sheets

    except Exception as e:
        print(f"[ASC] Error while computing Action Step Control: {e}")
        return None



def validate_dataframe(df: pd.DataFrame) -> tuple[bool, str | None]:
    """
    Validate DataFrame before processing.
    Returns tuple: (is_valid, error_message)
    """
    if df is None or df.empty:
        return False, "DataFrame is empty"

    if df.shape[0] == 0:
        return False, "No rows to process"

    if "wo_text_action.text" not in df.columns:
        candidates = [
            c for c in df.columns if "wo_text_action.text" in str(c).lower()
        ]
        if not candidates:
            return False, "No 'wo_text_action.text' column found in Excel file"

    return True, None


def extract_wp_value(df: pd.DataFrame) -> str:
    """
    Safely extract work package value from DataFrame.
    Looks for 'WP' column (case-insensitive).
    """
    wp_col = None
    for col in df.columns:
        if str(col).upper() == "WP":
            wp_col = col
            break

    if wp_col is None:
        print("   ⚠️ No 'WP' column found in Excel file")
        return "No_wp_found"

    wp_series = df[wp_col].dropna()
    if wp_series.empty:
        return "No_wp_found"

    wp_value = str(wp_series.iloc[0]).strip()
    if not wp_value or wp_value.upper() in ["N/A", "NA", "NONE", ""]:
        return "No_wp_found"

    return wp_value


def apply_date_filter(
        df: pd.DataFrame,
        filter_start_date: date | None = None,
        filter_end_date: date | None = None,
) -> pd.DataFrame:
    """
    Apply date filtering to DataFrame based on action_date column.

    Args:
        df: Input DataFrame
        filter_start_date: Optional start date (inclusive)
        filter_end_date: Optional end date (inclusive)

    Returns:
        Filtered DataFrame
    """
    if df.empty:
        return df

    # Find date columns (case-insensitive)
    action_date_col = None
    start_date_col = None
    end_date_col = None

    for col in df.columns:
        col_upper = str(col).upper()
        if col_upper == "ACTION_DATE":
            action_date_col = col
        elif col_upper == "START_DATE":
            start_date_col = col
        elif col_upper == "END_DATE":
            end_date_col = col

    if not action_date_col:
        print("   ⚠️ No action_date column found, skipping date filter")
        return df

    original_rows = len(df)

    # Convert action_date to datetime with hard-coded format YYYY-MM-DD
    df[action_date_col] = pd.to_datetime(
        df[action_date_col],
        format='%Y-%m-%d',
        errors='coerce'
    )

    # Show action_date range before filtering
    valid_dates = df[action_date_col].dropna()
    if not valid_dates.empty:
        print(f"   📊 ACTION_DATE range (before filter):")
        print(f"      Min: {valid_dates.min().date()}")
        print(f"      Max: {valid_dates.max().date()}")

    # Remove rows with invalid dates
    invalid_dates = df[action_date_col].isna().sum()
    if invalid_dates > 0:
        print(f"   ⚠️ Found {invalid_dates} rows with invalid date format - removing them")
        df = df[df[action_date_col].notna()]

    if df.empty:
        print("   ⚠️ All rows have invalid dates")
        return df

    # Get file's date range from start_date/end_date columns (FIRST ROW ONLY)
    file_start_date = None
    file_end_date = None

    if start_date_col:
        raw_start = df[start_date_col].iloc[0]
        start_ts = pd.to_datetime(
            raw_start,
            format='%Y-%m-%d',
            errors='coerce',
        )
        if not pd.isna(start_ts):
            file_start_date = start_ts

    if end_date_col:
        raw_end = df[end_date_col].iloc[0]
        end_ts = pd.to_datetime(
            raw_end,
            format='%Y-%m-%d',
            errors='coerce',
        )
        if not pd.isna(end_ts):
            file_end_date = end_ts

    # Show file's date range
    print(f"\n   📅 FILE DATE RANGE (from columns):")
    if file_start_date and not pd.isna(file_start_date):
        print(f"      start_date: {file_start_date.date()}")
    else:
        print(f"      start_date: NOT FOUND")

    if file_end_date and not pd.isna(file_end_date):
        print(f"      end_date: {file_end_date.date()}")
    else:
        print(f"      end_date: NOT FOUND")

    # PART 1: Auto-filter by file's date range
    print(f"\n   🔍 PART 1: Auto-filtering by file's date range...")

    if file_start_date and not pd.isna(file_start_date):
        before = len(df)
        df = df[df[action_date_col] >= file_start_date]
        removed = before - len(df)
        if removed > 0:
            print(f"      ✓ Removed {removed} rows before {file_start_date.date()}")
        else:
            print(f"      ℹ️ No rows removed (all >= {file_start_date.date()})")

    if file_end_date and not pd.isna(file_end_date):
        before = len(df)
        df = df[df[action_date_col] <= file_end_date]
        removed = before - len(df)
        if removed > 0:
            print(f"      ✓ Removed {removed} rows after {file_end_date.date()}")
        else:
            print(f"      ℹ️ No rows removed (all <= {file_end_date.date()})")

    # PART 2: User-specified filter
    if filter_start_date or filter_end_date:
        print(f"\n   👤 USER-SPECIFIED DATE FILTER:")
        if filter_start_date:
            print(f"      From: {filter_start_date}")
        if filter_end_date:
            print(f"      To: {filter_end_date}")

        print(f"\n   🔍 PART 2: Applying user filter...")

        if filter_start_date:
            before = len(df)
            df = df[df[action_date_col] >= pd.Timestamp(filter_start_date)]
            removed = before - len(df)
            if removed > 0:
                print(f"      ✓ Removed {removed} rows before {filter_start_date}")
            else:
                print(f"      ℹ️ No rows removed by start date filter")

        if filter_end_date:
            before = len(df)
            df = df[df[action_date_col] <= pd.Timestamp(filter_end_date)]
            removed = before - len(df)
            if removed > 0:
                print(f"      ✓ Removed {removed} rows after {filter_end_date}")
            else:
                print(f"      ℹ️ No rows removed by end date filter")

    # Show final action_date range
    valid_dates_after = df[action_date_col].dropna()
    if not valid_dates_after.empty:
        print(f"\n   📊 ACTION_DATE range (after filter):")
        print(f"      Min: {valid_dates_after.min().date()}")
        print(f"      Max: {valid_dates_after.max().date()}")

    filtered_rows = len(df)
    total_removed = original_rows - filtered_rows

    if total_removed > 0:
        print(f"\n   ✅ Date filter complete: {filtered_rows} rows remain ({total_removed} removed)")
    else:
        print(f"\n   ✅ No rows filtered (all within range)")

    # Convert back to string format
    df[action_date_col] = df[action_date_col].dt.strftime('%Y-%m-%d')

    return df


def load_and_filter_for_actions(
        file_path: str,
        filter_start_date: date | None = None,
        filter_end_date: date | None = None,
) -> tuple[pd.DataFrame, str]:
    """
    Prepare a DataFrame for Action Step Control WITHOUT ref/rev validation.

    Steps:
    - Read the Excel file using the standard settings
    - Apply the same date filter logic as the main validator
    - Return (filtered_df, wp_value)

    This keeps ASC separated from ref/rev Reason logic but reuses
    all the robust input/date handling.
    """
    print("\n" + "=" * 60)
    print("ACTION STEP CONTROL: PREPARING DATA")
    print("=" * 60)

    # 1) Read Excel
    print(f"\n1. Reading file for action control: {file_path}")
    df = read_input_excel(file_path)
    print(f"   ✓ Read {df.shape[0]} rows, {df.shape[1]} columns")

    # 2) Apply date filter (same rules)
    print("\n2. Applying date filter (file's start/end + optional user range)...")
    df = apply_date_filter(
        df,
        filter_start_date=filter_start_date,
        filter_end_date=filter_end_date,
    )

    if df.empty:
        print("   ✗ No data remains after date filtering")
        return df, "No_wp_found"

    print(f"   ✓ {len(df)} rows after date filtering")

    # 3) Extract WP (for folder naming or logging)
    wp_value = extract_wp_value(df)
    print(f"   ✓ Detected WP: {wp_value}")

    return df, wp_value


def _prepare_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename/create wo_text_action.text, SEQ, header columns as in original code."""
    # wo_text_action.text
    if "wo_text_action.text" not in df.columns:
        candidates = [
            c for c in df.columns if "wo_text_action.text" in str(c).lower()
        ]
        if candidates:
            df = df.rename(columns={candidates[0]: "wo_text_action.text"})
            print(f"   ✓ Renamed '{candidates[0]}' to 'wo_text_action.text'")
        else:
            df["wo_text_action.text"] = "N/A"
            print("   ⚠️ No wo_text_action.text column found, created empty column")

    df["wo_text_action.text"] = df["wo_text_action.text"].fillna("N/A").astype(str)

    # SEQ
    if "SEQ" not in df.columns:
        seq_candidates = [c for c in df.columns if str(c).upper() == "SEQ"]
        if seq_candidates:
            df = df.rename(columns={seq_candidates[0]: "SEQ"})
            print(f"   ✓ Found SEQ column: '{seq_candidates[0]}'")
        else:
            df["SEQ"] = None
            print("   ⚠️ No SEQ column found, validation will proceed normally")

    df["SEQ"] = df["SEQ"].fillna("")

    # HEADER
    if "wo_text_action.header" not in df.columns:
        header_candidates = [
            c for c in df.columns if "wo_text_action.header" in str(c).lower()
        ]
        if header_candidates:
            df = df.rename(columns={header_candidates[0]: "wo_text_action.header"})
            print(f"   ✓ Found header column: '{header_candidates[0]}'")
        else:
            df["wo_text_action.header"] = None
            print(
                "   ⚠️ No wo_text_action.header column found, "
                "validation will proceed normally"
            )

    df["wo_text_action.header"] = df["wo_text_action.header"].fillna("")

    # DES
    if "DES" not in df.columns:
        des_candidates = [c for c in df.columns if str(c).upper() == "DES"]
        if des_candidates:
            df = df.rename(columns={des_candidates[0]: "DES"})
            print(f"   ✓ Found DES column: '{des_candidates[0]}'")
        else:
            df["DES"] = None
            print(
                "   ⚠️ No DES column found, "
                "DES-based reference logic will treat rows "
                "as if no DES reference is present"
            )

    df["DES"] = df["DES"].fillna("")

    return df


def process_excel(
        file_path: str,
        filter_start_date=None,
        filter_end_date=None,
        enable_action_step_control: bool = ACTION_STEP_CONTROL_ENABLED_DEFAULT,
) -> str | None:
    """
    Process Excel file with multi-state validation and optional date filtering.

    Args:
        file_path: Path to Excel file
        filter_start_date: Optional start date for filtering
        filter_end_date: Optional end date for filtering

    Returns:
        Output Excel file path or None on error.
    """
    print("\n" + "=" * 60)
    print("PROCESSING EXCEL FILE")
    print("=" * 60)

    start_time = datetime.now()

    try:
        # ========== STEP 1: Read Excel File ==========
        print(f"\n1. Reading file: {file_path}")
        df = read_input_excel(file_path)
        print(f"   ✓ Read {df.shape[0]} rows, {df.shape[1]} columns")

        empty_rows = df[
            df.apply(lambda x: x.astype(str).str.strip().eq("").all(), axis=1)
        ]
        if not empty_rows.empty:
            print(f"   ⚠️ Found {len(empty_rows)} completely empty rows")

        # ========== STEP 2: Apply Date Filter (always) ==========
        step_num = 2
        print(f"\n{step_num}. Applying date filter "
              f"(file's start/end + optional user range)...")

        df = apply_date_filter(
            df,
            filter_start_date=filter_start_date,
            filter_end_date=filter_end_date,
        )

        # Snapshot for Action Step Control BEFORE validation mutates df
        df_for_action_step_control = df.copy()

        if df.empty:
            print("   ✗ No data remains after date filtering")
            return None

        print(f"   ✓ {len(df)} rows after date filtering")
        step_num += 1

        # ========== STEP 3: Validate DataFrame ==========
        is_valid, error_msg = validate_dataframe(df)
        if not is_valid:
            print(f"   ✗ Validation error: {error_msg}")
            return None

        orig_rows = df.shape[0]

        # ========== STEP 4: Prepare columns ==========
        print(f"\n{step_num}. Preparing data for validation...")
        df = _prepare_columns(df)
        step_num += 1

        # ========== STEP 5: Apply Validation ==========
        print(f"\n{step_num}. Validating documentation references...")
        print(
            "   ℹ️ SEQ 1.xx, 2.xx, 3.xx, 10.xx will be marked as Valid automatically"
        )
        print(
            "   ℹ️ Headers with CLOSE UP, JOB SET UP, "
            "OPEN/CLOSE ACCESS, GENERAL will be marked as Valid"
        )

        df["Reason"] = df.apply(
            lambda row: check_ref_keywords(
                row["wo_text_action.text"],
                row["SEQ"],
                row["wo_text_action.header"],
                row["DES"],
            ),
            axis=1,
        )

        print("   ✓ Validation complete")
        step_num += 1

        # ========== STEP 6: Statistics ==========
        counts = {
            "orig_rows": orig_rows,
            "out_rows": int(df.shape[0]),
            "Missing reference": int((df["Reason"] == "Missing reference").sum()),
            "Missing revision": int((df["Reason"] == "Missing revision").sum()),
            "Valid": int((df["Reason"] == "Valid").sum()),
            "N/A": int((df["Reason"] == "N/A").sum()),
            "header_auto_valid": int(
                df["wo_text_action.header"].apply(contains_header_skip_keyword).sum()
            )
        }

        # Header auto-valid count
        if counts["header_auto_valid"] > 0:
            print(
                f"      (includes {counts['header_auto_valid']} "
                f"header auto-valid rows)"
            )

        # SEQ auto-valid count
        counts["seq_auto_valid"] = int(df["SEQ"].apply(is_seq_auto_valid).sum())

        # Row mismatch check
        if counts["orig_rows"] != counts["out_rows"]:
            print("\n   🔴 CRITICAL: Row count mismatch detected!")
            print(f"      Original rows: {counts['orig_rows']}")
            print(f"      Output rows: {counts['out_rows']}")
            print(
                f"      LOST ROWS: "
                f"{counts['orig_rows'] - counts['out_rows']}"
            )
            save_debug_input_output(file_path, df)

        # Verify counts
        total_counted = sum(
            [
                counts["Valid"],
                counts["N/A"],
                counts["Missing reference"],
                counts["Missing revision"],
            ]
        )
        if total_counted != counts["out_rows"]:
            print("\n   ⚠️ WARNING: Count verification failed!")
            print(f"      Sum of categories: {total_counted}")
            print(f"      Total rows: {counts['out_rows']}")
            print("      This suggests an uncategorized reason exists!")

        # Display stats
        print(f"\n{step_num}. Validation Statistics:")
        print(f"   ✓ Valid: {counts['Valid']}")
        if counts["seq_auto_valid"] > 0:
            print(
                f"      (includes {counts['seq_auto_valid']} "
                f"SEQ auto-valid rows)"
            )
        if counts["header_auto_valid"] > 0:
            print(
                f"      (includes {counts['header_auto_valid']} "
                f"header auto-valid rows)"
            )

        print(f"   • N/A: {counts['N/A']}")
        print(f"   ✗ Missing reference: {counts['Missing reference']}")
        print(f"   ✗ Missing revision: {counts['Missing revision']}")

        total_errors = (
                counts["Missing reference"]
                + counts["Missing revision"]
        )
        print(f"\n   Total errors: {total_errors}")
        if counts["out_rows"] > 0:
            error_rate = (total_errors / counts["out_rows"]) * 100
            print(f"   Error rate: {error_rate:.1f}%")

        step_num += 1

        # ========== STEP 7: Prepare Output ==========
        print(f"\n{step_num}. Preparing output file...")
        wp_value = extract_wp_value(df)
        cleaned_folder_name, output_file = build_output_path(wp_value)
        step_num += 1

        # --- Action Step Control hook (stub for now) ---
        extra_sheets = run_action_step_control_hook(
            df=df_for_action_step_control,
            wp_value=cleaned_folder_name,
            source_file=file_path,
            enable_action_step_control=enable_action_step_control,
        )
        if extra_sheets:
            print(f"   [ASC] Extra sheets: {', '.join(extra_sheets.keys())}")
        else:
            print("   [ASC] Action Step Control disabled or not available")
        # ========== STEP 8: Write Excel ==========
        print(f"   Writing to: {output_file}")
        write_output_excel(df, output_file, extra_sheets=extra_sheets)

        # ========== STEP 9: Logbook ==========
        processing_time = (datetime.now() - start_time).total_seconds()
        append_to_logbook(cleaned_folder_name, counts, processing_time)

        # Summary
        print("\n" + "=" * 60)
        print("✓ PROCESSING COMPLETE")
        print("=" * 60)
        print(f"Output: {output_file}")
        print(f"Processing time: {processing_time:.2f} seconds")
        print("=" * 60 + "\n")

        return output_file

    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
