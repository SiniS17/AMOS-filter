# Project Refactor TODO

This document contains the full, detailed step-by-step plan for reorganizing the project into a clean, modular, multi-layer package structure.  
We will implement these changes together, module by module.

---

## PHASE 0 — Create Project Skeleton

### 0.1. Create new package layout (no logic changes yet)
- [X] Create folder: `doc_validator/`
- [X] Add empty `__init__.py`
- [X] Create subfolders (each with its own `__init__.py`):
  - [X] `doc_validator/core/`
  - [X] `doc_validator/validation/`
  - [X] `doc_validator/interface/`
  - [X] `doc_validator/tools/`
  - [X] `doc_validator/tests/`
- [X] Move existing `config.py` into `doc_validator/`

---

## PHASE 1 — Validation System Split (validators.py)

### 1.1. Split into new modules
**1.1.1. `validation/patterns.py`**  
Stores:
- All regex patterns  
- Compiled regex objects  
- Common keyword lists  
- Special markers (DOC IDs, SB number patterns, NDT patterns, etc.)

**1.1.2. `validation/helpers.py`**  
Contains:
- `fix_common_typos(text)`
- `contains_skip_phrase(text)`
- `has_data_module_task(text)`
- `has_ndt_report(text)`
- `has_sb_full_number(text)`
- `has_primary_reference(text)`
- `has_dmc_or_doc_id(text)`
- `has_revision(text)`
- `has_iaw_keyword(text)`
- Any other reusable pattern-matching helper

**1.1.3. `validation/engine.py`**  
Contains:
- `check_ref_keywords(text, seq_value=None)`  
- Exact rule order preserved  
- Imports helpers + patterns  
- No regex inside this file

### 1.2. Update imports
Change all modules that currently do:
```python
from validators import check_ref_keywords
```
to:
```python
from doc_validator.validation.engine import check_ref_keywords
```

---

## PHASE 2 — Excel Logic Split (excel_utils.py)

### 2.1. Create:

**2.1.1. `core/excel_io.py`**  
Responsible for:
- Reading Excel files
- Writing Excel files
- Writing CSV debug files
- Creating output and log paths
- `sanitize_folder_name()`  
- Ensuring output folder exists

**2.1.2. `core/excel_pipeline.py`**  
Responsible for:
- `extract_wp_value(df)`
- `validate_dataframe(df)`
- Using validation engine
- Creating processed output files
- Creating log files
- High-level: `process_excel(file_path)`

### 2.2. Integrate validation
In `excel_pipeline.py`, import:
```python
from doc_validator.validation.engine import check_ref_keywords
```

### 2.3. Update imports
Replace any old usage:
```python
import excel_utils
```
with:
```python
from doc_validator.core.excel_pipeline import process_excel
```
(or whichever function is needed)

---

## PHASE 3 — Drive I/O (drive_utils.py)

### 3.1. Create `core/drive_io.py`
Move these functions:
- `authenticate_drive_api(api_key)`
- `get_file_id_from_folder(drive_service, folder_id)`
- `download_file_from_drive(drive_service, file_id, wp_value)`
- `read_credentials_file(filename)`  
(may move to config if better)

### 3.2. Update imports
Replace:
```python
from drive_utils import (...)
```
with:
```python
from doc_validator.core.drive_io import (...)
```

---

## PHASE 4 — Core High-Level Pipeline

### 4.1. Create `core/pipeline.py`

Implement a unified function:
```python
def process_work_package(
    api_key,
    folder_id,
    *,
    logger=None,
    output_dir=None,
    download_dir=None,
    file_selector=None
):
```

Should:
- Authenticate Google Drive
- List Excel files in folder
- Select file (auto or callback)
- Download it
- Call `excel_pipeline.process_excel`
- Return:
  - processed file path
  - log path
  - debug file paths (optional)
- Forward progress to logger callback

---

## PHASE 5 — CLI Interface Layer

### 5.1. Create `interface/cli_main.py`

Contains:
- `def main():`
- Load credentials (API key, link.txt)
- Call core pipeline
- Print clean messages
- Handle errors cleanly
- Return exit code

### 5.2. Root runner script

Create `run_cli.py` in project root:

```python
from doc_validator.interface.cli_main import main

if __name__ == "__main__":
    raise SystemExit(main())
```

---

## PHASE 6 — Tests & Tools

### 6.1. Move tools
- Move `diagnose_row_loss.py` → `doc_validator/tools/diagnose_row_loss.py`
- Update imports inside it

### 6.2. Move tests
- Move all tests into: `doc_validator/tests/`
- Update imports:
  - `doc_validator.validation.engine`
  - `doc_validator.core.excel_pipeline`
  - etc.

---

## PHASE 7 — Optional GUI (Tkinter)

### 7.1. Create `interface/gui_tk.py`
GUI will:
- Let user select:
  - API key
  - link.txt
  - Drive folder ID
  - Local output folder
- Start pipeline in background thread
- Display log output
- Provide success/error messages

### 7.2. Root-level GUI runner (optional)
Create `run_gui.py`:

```python
from doc_validator.interface.gui_tk import launch

if __name__ == "__main__":
    launch()
```

---

## END OF TODO
This checklist will guide the refactor and ensure the project becomes modular, testable, and GUI-ready.
