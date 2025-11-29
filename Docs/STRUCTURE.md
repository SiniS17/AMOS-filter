# STRUCTURE – Modules and Responsibilities

This document summarises the code structure of the Documentation Validator project and the role of each file.

---

## 1. Top-Level Layout

```text
.
├── main.py
├── config.py
├── validators.py
├── excel_utils.py
├── drive_utils.py
├── diagnose_row_loss.py
├── test_validators.py
├── test_real_world_data.py
├── DATA/
└── log/
```

Additional folders may be created at runtime, such as:

- `DATA/<WP>/`      – per-work-package output directories.
- `DATA/<WP>/log/`  – per-work-package logs.
- `.../DEBUG/`      – debug exports (CSV) when row-mismatch is detected.

---

## 2. Module-by-Module Breakdown

### 2.1 `main.py` – Orchestration / Entry Point

**Purpose:** High-level script that wires everything together.

Responsibilities:

- Display a CLI banner and basic branding.
- Read API key and folder ID from `link.txt` via `drive_utils.read_credentials_file`.
- Authenticate to Google Drive with `drive_utils.authenticate_drive_api`.
- Find a file in the configured folder using `drive_utils.get_file_id_from_folder`.
- Download the file to the local `DATA` folder using `drive_utils.download_file_from_drive`.
- Call `excel_utils.process_excel` to validate and produce the final Excel + log.
- Print a completion message and return the final file path when successful.

Entry point is guarded by:

```python
if __name__ == "__main__":
    processed_file = main()
```

---

### 2.2 `config.py` – Global Configuration & Constants

**Purpose:** Central configuration for reference keywords, skip phrases, and folder names.

Key contents:

- `REASONS_DICT` – mapping of simplified validation reason labels for high-level descriptions.
- `REF_KEYWORDS` – list of primary reference keywords (AMM, SRM, CMM, EMM, SOPM, SWPM, IPD, FIM, TSM, IPC, SB, AD, MEL, NEF, MME, LMM, NTM, DWG, AIPC, DDG, VSB, etc.).
- `IAW_KEYWORDS` – linking words (IAW, REF, PER, I.A.W).
- `SKIP_PHRASES` – phrases that should bypass validation and be treated as valid by default (e.g. “GET ACCESS”, “SPARE ORDERED”, “OBEY ALL”).
- `INVALID_CHARACTERS` – regex for removing invalid filesystem characters from folder names.
- `DATA_FOLDER` – root directory for data (e.g. `DATA`).
- `LOG_FOLDER` – name of the log subfolder (e.g. `log`).
- `LINK_FILE` – name/path of the credentials file (e.g. `link.txt`).

All modules that need shared configuration import values from here.

---

### 2.3 `validators.py` – Core Validation Logic

**Purpose:** Implements the actual rule engine for classifying documentation text into validation states.

Main components:

1. **Regex Patterns**
   - General document ID patterns.
   - DMC-Like codes and B787 document patterns.
   - DATA MODULE TASK patterns.
   - Revision markers (REV, ISSUE, TAR, date formats).
   - NDT REPORT patterns, service bulletin patterns, etc.
   - “REFERENCED AMM/SRM” patterns.

2. **SEQ Auto-Validation**
   - `is_seq_auto_valid(seq_value)` – returns `True` if SEQ starts with 1., 2., 3., or 10.
   - If true, the entire row is immediately considered `Valid`.

3. **Helpers**
   - `fix_common_typos(text)` – normalises common typos (e.g. `REV156` ⇒ `REV 156`, missing spaces after reference keywords).
   - `contains_skip_phrase(text)` – checks for skip phrases from `config.SKIP_PHRASES`.
   - `has_referenced_pattern(text)` – detects “REFERENCED AMM/SRM/etc.” forms.
   - `has_ndt_report(text)` – detects “NDT REPORT <ID>”.
   - `has_sb_full_number(text)` – detects SB patterns with full part numbers.
   - `has_data_module_task(text)` – detects “DATA MODULE TASK <n>” shapes.
   - `has_primary_reference(text)` – checks for AMM/SRM/CMM/etc. from `config.REF_KEYWORDS`.
   - `has_dmc_or_doc_id(text)` – detects doc IDs (DMC, B787-style IDs, etc.).
   - `has_iaw_keyword(text)` – detects linking words (IAW, REF, PER).
   - `has_revision(text)` – detects revision markers (REV, ISSUE, EXP/DEADLINE dates, etc.).

4. **Main API Function**
   - `check_ref_keywords(text, seq_value=None)`
   - Returns one of:
     - `"Valid"`
     - `"Missing reference"`
     - `"Missing reference type"`
     - `"Missing revision"`
     - `"N/A"`

   Logic order:
   - SEQ auto-valid check → `Valid`.
   - N/A / blank preservation.
   - Skip phrases → `Valid`.
   - Fix typos and evaluate special patterns (REFERENCED, NDT REPORT, SB, DATA MODULE TASK).
   - Evaluate primary reference presence and DMC/doc IDs.
   - Evaluate revision presence.
   - Return the appropriate status.

This is the core rule-set for the entire project.

---

### 2.4 `excel_utils.py` – Excel I/O and Row-Level Pipeline

**Purpose:** Reads the Excel file, applies validation to every row, and writes the output file and log.

Key functions:

1. `sanitize_folder_name(wp_value)`
   - Cleans up the WP string so it can safely be used as a folder name.
   - Replaces invalid characters and returns a fallback if no usable string exists.

2. `create_log_file(wp_value, output_file, counts, processing_time=None)`
   - Writes a detailed `.txt` log in `DATA/<WP>/log/` summarising counts and performance.

3. `validate_dataframe(df)`
   - Ensures the DataFrame is not empty, has rows, and contains the necessary text column (or can infer it).

4. `extract_wp_value(df)`
   - Extracts the work package value from the `WP` column (case-insensitive), skipping empty or N/A-like values.

5. `process_excel(file_path)`
   - Orchestrates the entire Excel processing pipeline:
     - Reads the Excel file safely.
     - Prepares columns (`wo_text_action.text`, `SEQ`).
     - Applies `check_ref_keywords` row by row.
     - Computes per-status counters and SEQ auto-valid count.
     - Checks for row-count mismatches and outputs debug CSVs if needed.
     - Prepares a `Reason` column and writes the new Excel with hidden reference rows for filters.
     - Creates a log file via `create_log_file`.
     - Returns the path to the final Excel output file.

---

### 2.5 `drive_utils.py` – Google Drive Helper Functions

**Purpose:** Abstracts Google Drive operations so that other modules don’t need to know about API details.

Key functions:

- `authenticate_drive_api(api_key)`
  - Builds and returns a Drive v3 service client using a simple API key.

- `get_file_id_from_folder(drive_service, folder_id)`
  - Lists files under the given folder ID.
  - Returns the ID of the first file found (prints its name and ID).

- `download_file_from_drive(drive_service, file_id, wp_value)`
  - Creates `DATA/<wp_value>/` if necessary.
  - Downloads the file as `WP_<wp_value>_RAW.xlsx`.
  - Streams the content using `MediaIoBaseDownload`.

- `read_credentials_file(filename)`
  - Reads `GG_API_KEY=` and `GG_FOLDER_ID=` from `link.txt` (or a specified file).
  - Returns `(api_key, folder_id)` or `(None, None)` if the file is missing or malformed.

---

### 2.6 `diagnose_row_loss.py` – Row-Loss Diagnostic Tool

**Purpose:** Standalone CLI tool for investigating row-loss when reading Excel files.

Main function:

- `diagnose_file(file_path)`
  - Runs several `pandas.read_excel` calls with different parameter combinations (default, `keep_default_na=False`, `dtype=str`, production settings, updated settings, etc.).
  - Uses `openpyxl.load_workbook` to count non-empty rows in the worksheet directly.
  - Prints a summary showing rows read under each mode.
  - Recommends whichever mode yields the highest row count.

The script is invoked as:

```bash
python diagnose_row_loss.py <path_to_excel_file>
```

---

### 2.7 `test_validators.py` – Unit Tests for Validator Logic

**Purpose:** Self-contained test harness for the validation engine.

Characteristics:

- Implements a tiny `TestResults` helper class to track passed/failed tests.
- Covers scenarios such as:
  - N/A / blank preservation.
  - Skip-phrases becoming `Valid`.
  - Typo correction and recognition (`REFAMM52-11-01REV156`).
  - Proper classification of Missing reference / Missing revision.
  - Realistic examples from maintenance logs.
- Prints a test summary and an overall success/fail indication when run as a script.

Run with:

```bash
python test_validators.py
```

---

### 2.8 `test_real_world_data.py` – Real-World Data Tests

**Purpose:** Validates the behaviour of `check_ref_keywords` against known-good examples derived from actual customer data.

Key points:

- Uses the same simple `TestResults` pattern.
- Each test suite focuses on a category:
  - Valid references with AMM/SRM + DMC + REV.
  - Date-based revision formats (EXP/DEADLINE dates).
  - DMC-only or incomplete references (Missing reference type / Missing reference).
  - Work-step style entries with and without references.
  - NDT reports, service bulletins, data module tasks.
  - Edge cases like GENX AMM formats, referenced tasks, etc.
- At the end, prints:
  - Pass/fail counts.
  - Fail details (if any).
  - A short summary of the rule-set.

Run with:

```bash
python test_real_world_data.py
```

---

## 3. Runtime Directories

### 3.1 `DATA/`

- Root folder for all input and output work-package data.
- Each WP gets its own subfolder:

  ```text
  DATA/<WP>/
  ```

- Raw downloaded file:
  - `WP_<WP>_RAW.xlsx` (initial download – based on the placeholder WP used in `main.py`).

- Final processed output:
  - `WP_<WP>_<timestamp>.xlsx`.

### 3.2 `DATA/<WP>/log/`

- Text log files generated by `create_log_file`.
- Same basename as the final Excel, but with `.txt` extension.

### 3.3 `.../DEBUG/`

- Only present when the system detects a mismatch between original and processed row counts.
- Contains:
  - `input_original_<timestamp>.csv`
  - `output_processed_<timestamp>.csv`

These are meant for manual diffing and troubleshooting.

---

## 4. Extensibility

- New document families can be added by extending `REF_KEYWORDS` and adjusting `validators.py` patterns.
- Additional output formats (CSV, JSON) could be implemented in `excel_utils.py`.
- More advanced file-selection logic (e.g. by name/date) could be implemented in `main.py` / `drive_utils.py`.
- The current structure cleanly separates concerns, making it straightforward to add a CLI, REST API, or GUI layer on top in the future.
