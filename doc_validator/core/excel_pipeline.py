from datetime import datetime

import pandas as pd

from doc_validator.validation.engine import check_ref_keywords
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


def process_excel(file_path: str) -> str | None:
    """
    Process Excel file with multi-state validation.

    Returns output Excel file path or None on error.
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

        # ========== STEP 2: Validate DataFrame ==========
        is_valid, error_msg = validate_dataframe(df)
        if not is_valid:
            print(f"   ✗ Validation error: {error_msg}")
            return None

        orig_rows = df.shape[0]

        # ========== STEP 3: Prepare columns ==========
        print("\n2. Preparing data for validation...")
        df = _prepare_columns(df)

        # ========== STEP 4: Apply Validation ==========
        print("\n3. Validating documentation references...")
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
                row["wo_text_action.header"],  # header skip logic
                row["DES"],  # DES decides Missing reference
            ),
            axis=1,
        )

        print("   ✓ Validation complete")

        # ========== STEP 5: Statistics ==========
        counts = {"orig_rows": orig_rows, "out_rows": int(df.shape[0]),
                  "Missing reference": int((df["Reason"] == "Missing reference").sum()),
                  "Missing revision": int((df["Reason"] == "Missing revision").sum()),
                  "Valid": int((df["Reason"] == "Valid").sum()), "N/A": int((df["Reason"] == "N/A").sum()),
                  "header_auto_valid": int(
                      df["wo_text_action.header"].apply(contains_header_skip_keyword).sum()
                  )}

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
        print("\n4. Validation Statistics:")
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

        # ========== STEP 6: Prepare Output ==========
        print("\n5. Preparing output file...")
        wp_value = extract_wp_value(df)
        cleaned_folder_name = sanitize_folder_name(wp_value).replace(" ", "_")
        cleaned_folder_name, output_file = build_output_path(wp_value)

        # ========== STEP 7: Write Excel ==========
        print(f"   Writing to: {output_file}")
        write_output_excel(df, output_file)

        # ========== STEP 8: Logbook ==========
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

    except Exception as e:  # pragma: no cover - debugging path
        print(f"\n✗ ERROR: {str(e)}")
        import traceback

        traceback.print_exc()
        return None
