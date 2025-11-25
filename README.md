# AMOS-Filter / doc_validator

AMOS-Filter is a tool for validating documentation references inside maintenance Excel files.
It is built as a modular Python package called `doc_validator` and can be used via:

- A **CLI** (command-line interface)
- A **PyQt6 GUI**
- Direct module imports in your own code

The tool connects to a configured Google Drive folder, downloads Excel work packages,
runs a multi-state validation engine over each row, and writes filtered Excel outputs
plus summary logbooks.

---

## 1. Features

- ✅ Connect to a fixed Google Drive folder (configured in `link.txt`)
- ✅ List and download all Excel files from the folder
- ✅ Process selected files via GUI (checkboxes) or all files via CLI
- ✅ Multi-state validation of documentation references:
  - `Valid`
  - `Missing reference`
  - `Missing reference type`
  - `Missing revision`
  - `N/A`
- ✅ Special handling for:
  - AMM / SRM / CMM / MEL / DDG / EMM references
  - DMC & B787 document codes
  - NDT REPORT patterns
  - SB (Service Bulletin) references
  - DATA MODULE TASK patterns
- ✅ Safeguards against row loss with DEBUG CSV exports
- ✅ Monthly Excel logbook with statistics per run
- ✅ Tools for local batch processing and row-loss diagnosis
- ✅ PyQt6 GUI with:
  - File selection via checkboxes
  - Live console-style logging
  - Completion popup with output folder

---

## 2. Project Layout

The refactored project is organized as:

```text
doc_validator/
├── __init__.py
├── config.py
│
├── core/
│   ├── __init__.py
│   ├── drive_io.py          # Google Drive API access and file download
│   ├── excel_io.py          # Excel I/O, output paths, logbook, debug CSVs
│   ├── excel_pipeline.py    # High-level Excel processing for one file
│   └── pipeline.py          # Orchestrates Drive + Excel for batch runs
│
├── validation/
│   ├── __init__.py
│   ├── patterns.py          # Regex patterns and compiled objects
│   ├── helpers.py           # Utility checks (typos, skip phrases, patterns)
│   └── engine.py            # Main check_ref_keywords() decision logic
│
├── interface/
│   ├── __init__.py
│   ├── cli_main.py          # Command-line entry point
│   └── gui_qt.py            # PyQt6 GUI (file selection + log console)
│
├── tools/
│   ├── __init__.py
│   ├── process_local_batch.py  # Process all Excel files in a local folder
│   └── diagnose_row_loss.py    # Investigate row-loss issues in Excel I/O
│
└── tests/
    ├── __init__.py
    ├── test_validators.py      # Unit tests for validation engine
    └── test_real_world_data.py # Tests using real-world maintenance strings
```

At the project root you typically also have:

```text
run_cli.py        # convenience runner for the CLI
run_gui.py        # convenience runner for the GUI (optional)
TODO.md           # refactor checklist
STRUCTURE.md      # original structure notes
link.txt          # Google Drive credentials (not committed)
DATA/             # data root: raw WP folders, logs, debug CSVs
log/              # optional legacy log folder
```

---

## 3. Requirements & Installation

### 3.1. Python version

- Python **3.10+** (tested with 3.11)

### 3.2. Required packages

Install dependencies with `pip`:

```bash
pip install -r requirements.txt
```

Typical dependencies include:

- `pandas`
- `openpyxl`
- `google-api-python-client`
- `PyQt6`
- `numpy`
- `python-dateutil` (if used)
- plus any other libraries you already configured

---

## 4. Configuration

### 4.1. Credentials file (`link.txt`)

The Google Drive access is configured via a simple text file, usually at the project root:

```text
GG_API_KEY=YOUR_GOOGLE_API_KEY
GG_FOLDER_ID=YOUR_GOOGLE_DRIVE_FOLDER_ID
```

- `GG_API_KEY` — API key with access to Google Drive
- `GG_FOLDER_ID` — ID of the Google Drive folder containing Excel work packages

This file is read by:

- `doc_validator.core.drive_io.read_credentials_file`
- `doc_validator.core.pipeline.process_from_credentials_file`
- `doc_validator.interface.gui_qt.MainWindow` (indirectly via `LINK_FILE` in `config.py`)

You can adjust the default path via `LINK_FILE` constant in `config.py`.

### 4.2. Data folder (`DATA/`)

The `DATA/` folder (path also defined in `config.py`) is used to store:

- Downloaded raw Excel files (per work package)
- Processed Excel outputs
- DEBUG CSVs (input/output snapshots)
- Monthly Excel logbooks

Structure example:

```text
DATA/
├── temp_gui/
│   └── <raw files downloaded by GUI>
├── <WP_001>/
│   ├── WP_<WP_001>_<timestamp>.xlsx
│   └── log/
│       └── WP_<WP_001>_<timestamp>.txt   (optional legacy log)
└── log/
    └── logbook_YYYY_MM.xlsx              # monthly statistics
```

---

## 5. Usage

### 5.1. CLI usage

If you created `run_cli.py` at the root:

```bash
python run_cli.py
```

This will:

1. Read `GG_API_KEY` and `GG_FOLDER_ID` from `LINK_FILE` in `config.py`
2. Connect to Google Drive
3. Download **all** Excel files in the configured folder
4. Process each file with `process_excel`
5. Print a summary of successes/failures
6. Write outputs and logbook updates under `DATA/`

You can also run the CLI module directly:

```bash
python -m doc_validator.interface.cli_main
```

Optionally, pass a specific credentials file:

```bash
python -m doc_validator.interface.cli_main path/to/other_link.txt
```

---

### 5.2. GUI usage (PyQt6)

If you created `run_gui.py`:

```bash
python run_gui.py
```

or directly:

```bash
python -m doc_validator.interface.gui_qt
```

The GUI will:

1. Read credentials from `LINK_FILE` (`link.txt` by default)
2. Authenticate with Google Drive
3. List **all Excel files** in the configured folder
4. Show a table with:
   - A checkbox for each file
   - The file name
5. Let the user:
   - Select/deselect files
   - Click **Run** to process selected files
6. Display console-style log output in the bottom panel:
   - Mirrors `print()` output from the backend
7. When all processing is done:
   - Show a popup:  
     **"Data has been filtered"**  
     with the path to the first successful output directory

> Note: the user **cannot change the Drive folder** from the GUI.
> Folder selection is controlled by credentials and configuration only.

---

### 5.3. Local batch processing (without Drive)

You can also process a folder of local Excel files without using Google Drive:

```bash
python -m doc_validator.tools.process_local_batch "path/to/excel/folder"
```

This will:

- Scan the folder for `*.xls` / `*.xlsx` files
- Process each with `process_excel`
- Print a summary of successful and failed files

---

## 6. Validation Logic

The heart of the tool is `doc_validator.validation.engine.check_ref_keywords`.

### 6.1. Output states

Each row is classified as one of:

- `"Valid"`
- `"Missing reference"`
- `"Missing reference type"`
- `"Missing revision"`
- `"N/A"`

### 6.2. High-level rules (simplified)

1. If SEQ matches auto-valid patterns (e.g. `1.xx`, `2.xx`, `3.xx`, `10.xx`)  
   → `"Valid"` immediately.

2. If header contains skip keywords (e.g. `CLOSE UP`, `JOB SET UP`, `OPEN ACCESS`, etc.)  
   → `"Valid"`.

3. If text is `None` → `"N/A"`.  
   If text is `"N/A"`, `"NA"`, `"NONE"` or empty → preserved as-is.

4. If text contains skip phrases (e.g. `GAIN ACCESS`, `SPARE ORDERED`)  
   → `"Valid"`.

5. Typos are normalized (e.g. `REFAMM52-11-01REV156` becomes `REF AMM 52-11-01 REV 156`).

6. Special valid patterns:
   - `REFERENCED AMM/SRM/...`
   - `NDT REPORT <ID>`
   - `DATA MODULE TASK <N> + SB <full-number>` (if configured as valid)

7. If there is **no primary reference** (AMM/SRM/etc.):
   - And **no DMC/doc ID** → `"Missing reference"`
   - But **has DMC/doc ID** → `"Missing reference type"`

8. If there is a primary reference but **no revision** (REV/ISSUE/EXP/DEADLINE/DATE)  
   → `"Missing revision"`

This is intentionally strict to highlight missing documentation or incomplete references
so maintenance data can be cleaned and standardized.

---

## 7. Debugging & Diagnostics

### 7.1. Row-loss diagnosis

To investigate potential row-loss issues when reading/writing Excel files, use:

```bash
python -m doc_validator.tools.diagnose_row_loss path/to/file.xlsx
```

This tool will:

- Read the file with strict settings
- Inspect columns, types, empty rows
- Help identify where rows might be disappearing

### 7.2. Test suites

To run unit tests on the validation engine:

```bash
python -m doc_validator.tests.test_validators
```

To run tests based on real-world maintenance samples:

```bash
python -m doc_validator.tests.test_real_world_data
```

---

## 8. Development Notes

- The original codebase was a flat script (`main.py`, `validators.py`, `excel_utils.py`, `drive_utils.py`).
- It has been refactored into a **package** with clearly separated concerns:
  - Validation rules
  - Excel I/O
  - Drive I/O
  - Orchestration
  - Interfaces (CLI + GUI)
  - Tools and tests
- All new code should prefer importing from:
  - `doc_validator.validation.*`
  - `doc_validator.core.*`
  - `doc_validator.interface.*`

If you add new validation rules, prefer:

- Adding patterns to `validation/patterns.py`
- Adding helper checks to `validation/helpers.py`
- Updating decision flow in `validation/engine.py`
- Extending test coverage in `doc_validator/tests/`

---

## 9. License

This project is currently private / internal.
Add license information here if you plan to distribute it.
