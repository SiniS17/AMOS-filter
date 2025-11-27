# WORKFLOW – Documentation Validation Pipeline

This document describes the end-to-end data flow for the Documentation Validator, from Google Drive to the final Excel output and log file.

---

## 1. High-Level Overview

1. Read configuration from `link.txt` and `config.py`.
2. Authenticate with the Google Drive API using an API key.
3. Find a target Excel file in a configured Drive folder.
4. Download the file into a local `DATA` directory.
5. Read and validate the Excel content.
6. Write a cleaned Excel file and a detailed log (and optional debug files).

All orchestration is done in `main.py`, while specific logic is split into helper modules (`drive_utils.py`, `excel_utils.py`, `validators.py`).

---

## 2. Step-by-Step Workflow

### 2.1 Startup (`main.py`)

1. Print a banner (for CLI visibility).
2. Call `read_credentials_file("link.txt")` to get:
   - `GG_API_KEY`
   - `GG_FOLDER_ID`
3. If either is missing, abort with an error message.

### 2.2 Authenticate to Google Drive

- Use `authenticate_drive_api(api_key)` to create a Drive `service` object via the Google API client.
- All subsequent Drive operations go through this `service` instance.

### 2.3 Locate File in Folder

- Call `get_file_id_from_folder(service, folder_id)`.
- The function:
  - Lists all files whose parent is `folder_id`.
  - Takes the first file in the result set.
  - Prints the file name and ID for traceability.
- Returns the `file_id` (or `None` if the folder is empty).

### 2.4 Download Excel File

- Call `download_file_from_drive(service, file_id, wp_value="temp_download")`.
- The function:
  - Creates `DATA/temp_download/` if it does not exist.
  - Downloads the file as `DATA/temp_download/WP_temp_download_RAW.xlsx`.
  - Uses a streamed download via `MediaIoBaseDownload`.
- Returns the local file path.

At this point, we have the raw Excel file on disk.

---

## 3. Excel Processing & Validation

All content processing is handled in `excel_utils.process_excel(file_path)`.

### 3.1 Safe Excel Read

The tool reads the Excel sheet with settings designed to prevent row loss and preserve strings:

```python
df = pd.read_excel(
    file_path,
    engine="openpyxl",
    header=0,
    sheet_name=0,
    keep_default_na=False,
    dtype=str,
    na_filter=False,
)
```

Diagnostics:
- Prints number of rows and columns.
- Checks for completely empty rows (all empty strings) and logs how many exist.

### 3.2 DataFrame Validation

Before continuing, `validate_dataframe(df)` checks for basic requirements:

- DataFrame is not empty.
- At least one data row.
- A column named `wo_text_action.text` must exist, or a close match is found and renamed.
- If validation fails, the function prints an error and returns `None` (abort).

### 3.3 Column Normalisation

1. **Text column (`wo_text_action.text`)**
   - If not present, the code tries to find a similar column name (case-insensitive).
   - If still not found, a new column is created and filled with `"N/A"`.
   - All values are converted to string, with `NaN` replaced by `"N/A"`.

2. **Sequence column (`SEQ`)**
   - If not present, the code looks for any column whose uppercase name is `SEQ` and renames it.
   - If none exists, a new `SEQ` column is created with empty strings.
   - All `NaN` values are replaced with empty strings.

### 3.4 Work Package Extraction

- `extract_wp_value(df)` looks for a `WP` column (case-insensitive) and takes the **first non-empty, non-N/A** value.
- That value is then sanitised via `sanitize_folder_name()` to remove illegal filesystem characters, and spaces are replaced with `_`.
- If no usable WP can be found, `"No_wp_found"` is used.

### 3.5 Row-Level Validation

For each row, the validator logic is applied:

```python
df["Reason"] = df.apply(
    lambda row: check_ref_keywords(row["wo_text_action.text"], row["SEQ"]),
    axis=1,
)
```

`check_ref_keywords(text, seq)` performs these checks in order:

1. **SEQ auto-valid** – if `SEQ` begins with `1.`, `2.`, `3.`, or `10.`, returns `"Valid"` immediately.
2. **Preserve N/A / blank** – if text is `None`, a float, or “N/A” / “NA” / “NONE” / `""`, returns `N/A` or the original casing.
3. **Skip phrases** – if the text contains configured skip phrases (e.g. “GET ACCESS”), returns `"Valid"`.
4. **Fix common typos** – normalises patterns like `REV156` ⇒ `REV 156`, `REFAMM` ⇒ `REF AMM`.
5. **Special patterns**:
   - REFERENCED + AMM/SRM/etc.
   - NDT REPORT + doc ID.
   - DATA MODULE TASK + SB.
   - SB with full number and linking word.
6. **Primary reference detection** – checks for any of the reference keywords from `config.REF_KEYWORDS`.
7. **DMC/doc ID detection** – checks for DMC, B787-style IDs, or data-module-like descriptors.
8. **Revision detection** – checks for `REV`, `ISSUE`, `EXP`/`DEADLINE` dates, etc.
9. **Classification**:
   - No primary reference & no DMC/doc ID → `"Missing reference"`.
   - No primary reference but has DMC/doc ID → `"Missing reference type"`.
   - Has primary reference but no revision → `"Missing revision"`.
   - Otherwise → `"Valid"`.

### 3.6 Statistics & Consistency Checks

The script builds a `counts` dictionary with:

- Total original rows (`orig_rows`).
- Total output rows (`out_rows`).
- Count of each status:
  - `Valid`
  - `N/A`
  - `Missing reference`
  - `Missing reference type`
  - `Missing revision`
- Count of SEQ auto-valid rows (`seq_auto_valid`).

Checks performed:

1. **Row count mismatch** – if `orig_rows != out_rows`:
   - Prints a critical warning.
   - Creates a `DEBUG/` folder next to the file.
   - Writes `input_original_<timestamp>.csv` and `output_processed_<timestamp>.csv` for manual comparison.
2. **Category sum vs total rows** – if the sum of all categories does not equal `out_rows`, prints a warning that some rows may not be classified correctly.

---

## 4. Output Generation

### 4.1 Output File Path

- A folder `DATA/<sanitised_WP>/` is created (if needed).
- The final file is named:

  ```text
  WP_<sanitised_WP>_<timestamp>.xlsx
  ```

  where `<timestamp>` is something like `03pm45_21_11_25` (12-hour lowercased with date).

### 4.2 Writing Excel

Using `pd.ExcelWriter` with `openpyxl`:

1. The full DataFrame (including the new `Reason` column) is written.
2. The workbook / active sheet handle is obtained from the writer.
3. The code finds the column index of `Reason`.
4. For each of the possible Reason values:

   ```text
   - Valid
   - Missing reference
   - Missing reference type
   - Missing revision
   - N/A
   ```

   it appends a new row at the bottom, writes the Reason into that column, and marks the row as hidden.

5. An AutoFilter is applied over the entire used range to ensure Excel’s filter dropdown includes the hidden reference rows.

Finally, the workbook is saved.

### 4.3 Log File Creation

- `create_log_file(wp_value, output_file, counts, processing_time)` is called.
- It creates `DATA/<WP>/log/` if necessary.
- Writes a human-readable text report including:
  - Header and metadata (output file, timestamp, WP).
  - Original vs output row count and any mismatch warnings.
  - SEQ auto-valid counts.
  - Per-category counts for validation statuses.
  - Total errors and error rate %.
  - Processing time in seconds.

---

## 5. Diagnostic Workflow (Optional)

`diagnose_row_loss.py` can be run manually to investigate row-loss issues:

1. Accepts an Excel path as an argument.
2. Reads it with several different `read_excel` parameter combinations.
3. Uses `openpyxl` directly to count non-empty rows.
4. Prints a summary table indicating which method yields the highest row count and recommends that configuration.

This script is intended as a troubleshooting helper and is not called by `main.py` automatically.

---

## 6. Error Handling Overview

- Missing API key / folder ID → early exit with an error message.
- Empty DataFrame / missing text column → abort processing with a validation error message.
- Row count mismatch → still produces output, but also generates debug CSVs and prints warnings.
- Unexpected exceptions in `process_excel` are printed with a stack trace and result in `None` being returned to the caller.
