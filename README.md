# Documentation Validator – Automated Excel Reference Validation Tool

This project is a Python-based tool for validating aircraft maintenance documentation references in Excel work packages.

It will:

- Download an Excel file from a specified Google Drive folder.
- Parse and validate each maintenance text entry.
- Classify rows into several validation states (Valid / Missing reference / Missing reference type / Missing revision / N/A).
- Generate a cleaned Excel output file and a detailed validation log per work package.

---

## 1. Features

### 1.1 Google Drive Integration
- Reads an API key and folder ID from a simple `link.txt` file.
- Uses the Google Drive v3 API to list files in the configured folder and select a file to process.
- Downloads the file into a structured `DATA/<WP>/` folder as `WP_<WP>_RAW.xlsx`.

Core implementation: `drive_utils.py`, `main.py`.

### 1.2 Robust Excel Processing
- Reads Excel with **no row loss** using:

  ```python
  pd.read_excel(
      file_path,
      engine="openpyxl",
      header=0,
      sheet_name=0,
      keep_default_na=False,
      dtype=str,
      na_filter=False,
  )
  ```

- Normalises critical columns:
  - Work text column: `wo_text_action.text` (renamed/created if necessary).
  - Sequence column: `SEQ` (renamed/created if necessary).

Core implementation: `excel_utils.py`.

### 1.3 Validation Engine
Validation logic is centralised in `validators.py` and driven by configuration in `config.py`:

- Uses keyword sets for reference documents (AMM, SRM, CMM, EMM, SB, AD, MEL, NEF, etc.).
- Uses linking keywords (IAW, REF, PER, etc.).
- Uses skip-phrases where references are not required (e.g. “GET ACCESS”, “SPARE ORDERED”, “FOLLOW ALL”).

The main function `check_ref_keywords(text, seq_value=None)` returns one of:

- `Valid`
- `Missing reference`          – no reference documents at all
- `Missing reference type`     – has DMC/doc ID but no AMM/SRM/etc.
- `Missing revision`           – has reference but missing REV/ISSUE/EXP date
- `N/A`                        – blank or N/A-style entries

Special patterns handled as Valid when correctly formed include:

- REFERENCED AMM/SRM patterns.
- NDT REPORT with ID.
- Service Bulletin (SB) with full number.
- DATA MODULE TASK + SB combinations.

### 1.4 SEQ Auto-Validation

Certain SEQ ranges are considered auto-valid regardless of text content:

- Any SEQ value starting with `1.`
- Any SEQ value starting with `2.`
- Any SEQ value starting with `3.`
- Any SEQ value starting with `10.`

For these rows, `check_ref_keywords` will immediately return `Valid`.

### 1.5 Output & Logging

For each processed file, the tool produces:

1. **New Excel file** in `DATA/<WP>/` named:
   ```
   WP_<WP>_<timestamp>.xlsx
   ```

   Additional behaviour:
   - Adds a `Reason` column with the validation outcome for each row.
   - Writes a set of hidden rows containing *all possible* Reason values so that Excel’s filter dropdown always contains every status (even if some don’t appear in the dataset).
   - Applies an AutoFilter over the full data range.

2. **Log file** in `DATA/<WP>/log/` with:
   - Original vs output row counts.
   - Number of rows per category (Valid, N/A, Missing reference, Missing reference type, Missing revision).
   - Count of SEQ auto-valid rows.
   - Error rate (%).
   - Processing time.

3. **Optional debug CSVs** (if row count mismatch detected):
   - Original input CSV.
   - Processed output CSV.
   - Saved under a `DEBUG/` subfolder adjacent to the original file.

### 1.6 Diagnostic Tool for Row Loss

A separate script, `diagnose_row_loss.py`, is provided to help investigate any suspected row-loss problems when reading Excel files. It:

- Tries multiple combinations of `read_excel` parameters.
- Compares row counts across methods.
- Uses `openpyxl` directly to count non-empty rows at the sheet level.

---

## 2. Project Layout

See `STRUCTURE.md` for a full breakdown, but at a high level:

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

---

## 3. Installation

### 3.1 Python Environment

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
# or
.venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

If you don’t have a `requirements.txt` yet, a minimal set is:

```text
pandas
openpyxl
google-api-python-client
```

### 3.2 Google Drive API

1. Create / get an API key for Google Drive v3.
2. Create a Google Drive folder and put the input Excel file in it.
3. Create a `link.txt` in the project root with:

   ```text
   GG_API_KEY=your_api_key_here
   GG_FOLDER_ID=your_folder_id_here
   ```

The tool will read this file automatically at runtime.

---

## 4. Usage

### 4.1 End-to-End Run

From the project root:

```bash
python main.py
```

The script will:

1. Read API key and folder ID from `link.txt`.
2. Authenticate Google Drive.
3. List and select the first file in the configured folder.
4. Download it into `DATA/temp_download/` as `WP_temp_download_RAW.xlsx`.
5. Process the Excel file and infer the real WP value from the `WP` column.
6. Save the validated output under `DATA/<WP>/` and create a log file under `DATA/<WP>/log/`.

### 4.2 Running Only the Validator Tests

```bash
python test_validators.py
python test_real_world_data.py
```

- `test_validators.py` focuses on unit-level behaviours (typo correction, revision detection, skip phrases, etc.).
- `test_real_world_data.py` runs multiple realistic strings taken from actual customer data to ensure the rules behave as expected.

### 4.3 Row-Loss Diagnostic

If you suspect rows are being lost at the Excel reading stage, run:

```bash
python diagnose_row_loss.py path/to/file.xlsx
```

This will print a comparative summary of row counts under various reading modes and highlight which one preserves the maximum number of rows.

---

## 5. Configuration

All configurable constants live in `config.py`, including:

- `REF_KEYWORDS` – the list of document types to be treated as “primary” references (AMM, SRM, CMM, etc.).
- `IAW_KEYWORDS` – linking terms like `IAW`, `REF`, `PER`.
- `SKIP_PHRASES` – phrases that should be auto-marked as Valid without reference checking.
- `DATA_FOLDER` – root for data and outputs (default: `DATA`).
- `LOG_FOLDER` – subfolder for logs (default: `log`).
- `INVALID_CHARACTERS` – regex for sanitising folder/file names.

To adjust the rule-set for your organisation, you normally only need to edit `config.py` and, if necessary, tweak `validators.py`.

---

## 6. Limitations & Future Work

- Only the first file in the Google Drive folder is processed; more complex file selection (e.g. by name/date) can be added.
- Current validator is tailored to AMM/SRM/EMM-style documentation; additional document families can be plugged into the keyword config.
- GUI / web front-end is not included yet; this version focuses purely on the backend batch validator.

---

## 7. License

Internal use only (VAECO / maintenance engineering tooling).
