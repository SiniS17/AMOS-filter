# AMOSFilter – Aircraft Documentation Validator  
**Version:** 2.1.6  
**Language:** Python 3.10+  
**GUI:** PyQt6  
**Platforms:** Windows / Linux / macOS

AMOSFilter is a documentation validation tool designed for aircraft maintenance work packages (Excel format).  
It provides structured validation, date range filtering, and automated output generation with a modern PyQt6 GUI.

---

## ⚡ Key Features

### 🔍 Validation Engine
- Detects 20+ aviation document types (AMM, SRM, CMM, MEL, DDG, EMM, SB, DMC…)
- 4-state validation result:
  - **Valid**
  - **Missing reference**
  - **Missing revision**
  - **N/A**
- Auto-correction of common formatting issues
- Skip-logic for SEQ tasks and maintenance section headers

### 📅 Smart Date Filtering
- Optional user-defined date range
- Supports absolute (`2025-01-22`) and relative (`-7d`, `+1m`) formats
- Automatically clamps to file’s date range
- Two-stage filtering with console output logging

### 🖥️ Modern GUI (v2.1.6)
- Two-column layout (Input Source + Date Filter → File Table + Console)
- PNG logo branding
- Large refresh icon embedded in table header
- Browse & Open Output actions in Input Source panel
- Cleaner spacing, compact components, improved usability
- Collapsible console panel

### 📂 Input Sources
- Local folders (`INPUT/`)
- Optional Google Drive integration (API key + folder ID)

### 📁 Output
- Processed Excel files written to `DATA/<WP_NAME>/`
- Auto-filter enabled output
- Per-run monthly logbook stored in `DATA/log/`

---

## 📦 Installation

```bash
git clone <repository-url>
cd AMOSFilter
pip install -r requirements.txt
```

Required packages include:

```
pandas
openpyxl
PyQt6
numpy
google-api-python-client
python-dateutil
```

---

## ▶️ Running the Application

### GUI Mode (Recommended)
```bash
python run_gui.py
# or
python -m doc_validator.interface.main_window
```

### CLI Mode
```bash
python -m doc_validator.interface.cli_main
```

### Process a Local Folder (CLI)
```bash
python -m doc_validator.tools.process_local_batch "./path/to/files"
```

---

## 🗂️ Project Structure

```
doc_validator/
├── core/               # Drive I/O, Excel I/O, pipeline logic
├── validation/         # Regex patterns, rules, validator engine
├── interface/          # GUI (PyQt6) and CLI
│   ├── panels/         # Input Source panel, Date Filter panel
│   ├── widgets/        # SmartDateLineEdit
│   └── workers/        # Background threading worker
├── tools/              # Standalone scripts
└── tests/              # Unit tests
```

---

## ⚙️ Configuration

Google Drive settings are stored in:

```
bin/link.txt
```

Example:

```
GG_API_KEY=YOUR_API_KEY
GG_FOLDER_ID=YOUR_FOLDER_ID
```

---

## 📚 Documentation

Full documentation is located under the `/docs/` directory:

- `docs/USER_GUIDE.md`
- `docs/DEVELOPER_GUIDE.md`
- `docs/DATE_FILTERING.md`
- `docs/VALIDATION_RULES.md`
- `docs/CHANGELOG.md`

---

## 📝 Changelog

### v2.1.6 — GUI Redesign
- New header logo (PNG)
- Two-column layout
- Table header refresh icon
- Compact Input Source panel
- Simplified Date Filter panel
- Removed legacy toolbar
- Refined spacing and margins

See full changelog in `/docs/CHANGELOG.md`.

---

## 📄 License
Private / Internal Use Only  
Unauthorized distribution is prohibited.
