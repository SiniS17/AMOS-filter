# AMOSFilter / Documentation Validator

**AMOSFilter** is a professional tool for validating aircraft maintenance documentation references in Excel work packages. It features a modern PyQt6 GUI, multi-threaded processing, smart date filtering, and comprehensive validation rules for aviation maintenance standards.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-Private-red)

---

## 📋 Table of Contents

- [Features](#-features)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Validation Logic](#-validation-logic)
- [Date Filtering](#-date-filtering)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [Changelog](#-changelog)

---

## ✨ Features

### 🎨 **Modern GUI (Phase 1 & 2 Complete)**
- ✅ **Dark theme** with professional styling
- ✅ **File details columns** (size, modified date, status)
- ✅ **Real-time progress tracking** with percentage and status
- ✅ **Collapsible console** output for better space management
- ✅ **Search bar** for filtering files by name
- ✅ **Toggle-style checkboxes** with smooth animations
- ✅ **Status indicators** (✓ Success, ✗ Failed) after processing

### 📂 **Flexible Input Sources**
- 📁 **Local folder** processing (default: `INPUT/` folder)
- ☁️ **Google Drive** integration with API key authentication
- 🔄 **One-click refresh** without restarting the app
- 🔍 **Browse** to any local folder on your system

### 📅 **Smart Date Filtering**
- 🗓️ **Two-layer filtering**:
  1. Automatic pre-filter (removes rows outside file's date range)
  2. User-specified filter with smart validation
- ⌨️ **Flexible input formats**:
  - Absolute: `2025-11-27`
  - Relative: `-1d`, `+2d`, `-1m`, `+1y`
- 🎯 **Auto-adjustment** to file's valid date range
- 📊 **Detailed logging** of filtering results

### 🔍 **Comprehensive Validation**
- ✅ **4-state validation system**:
  - `Valid` - Complete documentation with reference and revision
  - `Missing reference` - No reference documents found
  - `Missing revision` - Has reference but missing REV/ISSUE/DATE
  - `N/A` - Blank or explicitly marked N/A
- 🛫 **Aviation-specific patterns**:
  - AMM/SRM/CMM/MEL/DDG/EMM and 20+ document types
  - DMC (Data Module Code) recognition
  - NDT REPORT patterns
  - Service Bulletin (SB) full numbers
  - DATA MODULE TASK references
- 🔧 **Auto-correction** of common typos
- 📝 **SEQ auto-valid** (1.xx, 2.xx, 3.xx, 10.xx)
- 🏷️ **Header skip keywords** (CLOSE UP, JOB SET UP, etc.)

### ⚡ **Performance & Reliability**
- 🧵 **Multi-threaded processing** (non-blocking UI)
- 📊 **Line-count based progress** tracking
- ❌ **Cancel button** to stop processing mid-run
- 💾 **Monthly Excel logbook** with statistics
- 🐛 **Debug CSV exports** for row-loss diagnosis
- 📈 **Error rate calculation** and reporting

### 📁 **Output Management**
- 📂 **Organized output structure** under `DATA/` folder
- 📊 **Auto-filter enabled** Excel files for easy filtering
- 📋 **Monthly logbook** tracking all processing runs
- 🔍 **Open output folder** button for quick access
- 📝 **Console logging** with detailed progress information

---

## 📸 Screenshots

### Main Window (Dark Theme)
```
┌─────────────────────────────────────────────────────────┐
│ ✈️ AMOSFilter                           v2.0 Phase 2    │
├─────────────────────────────────────────────────────────┤
│ 📂 Input Source                                         │
│ Load from: [📁 Local Folder ▼] [📁 Browse...]          │
│ Folder: C:\Users\...\INPUT                              │
├─────────────────────────────────────────────────────────┤
│ 🔄 Refresh    📁 Open Output                            │
├─────────────────────────────────────────────────────────┤
│ 📅 Date Filter (Optional)                               │
│ ☐ Enable date filtering                                │
│ From: [2024-10-27] 📅  To: [2025-11-27] 📅             │
├─────────────────────────────────────────────────────────┤
│ 🔍 [Search files by name...]                            │
├─────────────────────────────────────────────────────────┤
│ 📊 Excel Files                                          │
│ ┌─┬────────────┬────────┬──────┬──────────┬────────┐   │
│ │☐│File Name   │Source  │Size  │Modified  │Status  │   │
│ ├─┼────────────┼────────┼──────┼──────────┼────────┤   │
│ │☑│WP_001.xlsx │📁 Local│1.2 MB│2025-11-27│✓Success│   │
│ │☑│WP_002.xlsx │📁 Local│856 KB│2025-11-26│        │   │
│ └─┴────────────┴────────┴──────┴──────────┴────────┘   │
│ [✓ Select All] [✗ Deselect All]      [▶ Run Processing]│
├─────────────────────────────────────────────────────────┤
│ Progress: 67%                                           │
│ [████████████████░░░░░░░░░] Processing file 2/3...      │
├─────────────────────────────────────────────────────────┤
│ 📝 Console Output                         [▼ Collapse]  │
│ ┌─────────────────────────────────────────────────────┐ │
│ │✓ Found 3 Excel file(s)                              │ │
│ │📅 Filter: 2024-10-27 to 2025-11-27                  │ │
│ │[1/3] WP_001.xlsx                                    │ │
│ │   ✓ Date filter complete: 1243 rows remain         │ │
│ │   ✓ Valid: 1156  • N/A: 42  ✗ Missing ref: 45     │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation

### Prerequisites
- **Python 3.10+** (tested with 3.11)
- **Windows / macOS / Linux**

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd AMOSFilter
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

**Required packages:**
```
pandas>=2.0.0
openpyxl>=3.1.0
google-api-python-client>=2.0.0
PyQt6>=6.5.0
numpy>=1.24.0
python-dateutil>=2.8.0
```

### Step 3: Configure Credentials
Create `bin/link.txt` for Google Drive access:
```
GG_API_KEY=your_google_api_key_here
GG_FOLDER_ID=your_google_drive_folder_id
```

### Step 4: Create Input Folder
```bash
mkdir INPUT
```
Place your Excel files here for local processing.

---

## ⚡ Quick Start

### GUI Mode (Recommended)
```bash
python run_gui.py
```

**Or:**
```bash
python -m doc_validator.interface.main_window
```

### CLI Mode (Batch Processing)
```bash
python -m doc_validator.interface.cli_main
```

### Local Folder Processing
```bash
python -m doc_validator.tools.process_local_batch "path/to/excel/folder"
```

---

## 📖 Usage

### Basic Workflow

1. **Launch GUI**
   ```bash
   python run_gui.py
   ```

2. **Select Input Source**
   - Choose "📁 Local Folder" or "☁️ Google Drive"
   - Browse to select folder (for local) or use configured Drive folder

3. **Optional: Enable Date Filter**
   - Check "Enable date filtering"
   - Set date range: `From: 2024-01-01  To: 2025-12-31`
   - Or use relative dates: `-30d` (30 days ago), `+7d` (7 days from now)

4. **Select Files**
   - Use checkboxes to select files
   - Or click "✓ Select All"
   - Use search bar to filter: type "WP_001" to show only matching files

5. **Run Processing**
   - Click "▶ Run Processing"
   - Watch progress bar and console output
   - Status column updates with ✓ Success or ✗ Failed

6. **Access Results**
   - Click "📁 Open Output" to open `DATA/` folder
   - Find processed files in `DATA/WP_XXX/` folders
   - Check `DATA/log/logbook_YYYY_MM.xlsx` for statistics

---

## 🔍 Validation Logic

### 4-State System

#### ✅ **Valid**
Has complete documentation reference with revision:
```
✓ IAW AMM 52-11-01 REV 156
✓ REF SRM 54-21-03 ISSUE 002
✓ PER CMM 32-42-11 REV 45
✓ IAW MEL 33-44-01-02A, DEADLINE: 01/11/2025
✓ REF NDT REPORT NDT02-251067
✓ DATA MODULE TASK 2, SB B787-A-21-00-0128-02A-933B-D
✓ REFERENCED AMM TASKS
```

#### ❌ **Missing reference**
No reference documents found:
```
✗ INSPECTED PANEL
✗ REMOVED AND REPLACED COMPONENT
✗ WORK COMPLETED SATISFACTORILY
```

#### ❌ **Missing revision**
Has reference but missing REV/ISSUE/DATE:
```
✗ IAW AMM 52-11-01  (no REV)
✗ REF SRM 54-21-03  (no ISSUE)
✗ PER CMM 32-42-11  (no revision number)
```

#### • **N/A**
Blank or explicitly marked:
```
• N/A
• (blank)
• None
```

### Special Patterns

#### **SEQ Auto-Valid**
Automatically marked as Valid:
- `1.xx` (e.g., 1.1, 1.10, 1.25)
- `2.xx` (e.g., 2.5, 2.99)
- `3.xx` (e.g., 3.12)
- `10.xx` (e.g., 10.1, 10.50)

#### **Header Skip Keywords**
Rows with these headers are marked as Valid:
- CLOSE UP / CLOSEUP
- JOB SET UP / JOB SETUP
- OPEN ACCESS / CLOSE ACCESS
- GENERAL

#### **Skip Phrases**
Automatically valid if text contains:
- GET ACCESS / GAIN ACCESS
- SPARE ORDERED
- OBEY ALL / FOLLOW ALL
- SEE FIGURE / REFER TO FIGURE

### Supported Document Types

**Primary References (20+ types):**
- AMM (Aircraft Maintenance Manual)
- SRM (Structural Repair Manual)
- CMM (Component Maintenance Manual)
- MEL (Minimum Equipment List)
- DDG (Dispatch Deviation Guide)
- EMM (Engine Maintenance Manual)
- NEF, MME, LMM, NTM, DWG, AIPC, AMMS
- BSI, FIM, FTD, TIPF, MNT, EEL VNA, EO EOD

**Document Formats:**
- DMC (Data Module Code): `DMC-B787-A-52-09-01-00A-280A-A`
- B787 Format: `B787-A-G71-11-01-00A-720A-A`
- SB Full Number: `SB B787-A-21-00-0128-02A-933B-D`
- NDT Report: `NDT REPORT NDT02-251067`

**Revision Formats:**
- `REV 156`, `REV: 45`, `REV. 23`
- `ISSUE 002`, `ISSUED SD. 12`
- `TAR 45`
- `EXP 03JAN25`, `EXP: 28/06/2026`
- `DEADLINE: 01/11/2025`

### Auto-Correction

Common typos are automatically fixed:
```
REFAMM52-11-01REV156  →  REF AMM 52-11-01 REV 156
IAWAMMrev45           →  IAW AMM rev 45
REFCMM  32-42-11      →  REF CMM 32-42-11
```

---

## 📅 Date Filtering

### Two-Layer System

#### **Layer 1: Automatic Pre-Filter**
Removes rows outside the file's own date range:
```python
if action_date < start_date:  # Remove
if action_date > end_date:    # Remove
```

#### **Layer 2: User Filter**
User-specified dates with smart validation:
```python
# User picks dates, but they're auto-adjusted:
if user_start < file_start_date:
    user_start = file_start_date  # Clamp to file's range

if user_end > file_end_date:
    user_end = file_end_date  # Clamp to file's range
```

### Date Input Formats

#### **Absolute Dates**
```
2025-11-27
2024-01-01
2026-12-31
```

#### **Relative Dates**
```
-1d    # Yesterday
+7d    # 7 days from now
-1m    # 1 month ago
+3m    # 3 months from now
-1y    # 1 year ago
+2y    # 2 years from now
```

### Example Scenario
```
File date range:  2025-10-01 to 2025-10-22
User picks:       2025-09-01 to 2025-11-01

Auto-adjusted to: 2025-10-01 to 2025-10-22
```

### Console Output
```
📅 Date filter enabled:
   From: 2025-10-01
   To: 2025-10-22

📊 ACTION_DATE range (before filter):
   Min: 2025-09-15
   Max: 2025-11-05

🔍 PART 1: Auto-filtering by file's date range...
   ✓ Removed 15 rows before 2025-10-01
   ✓ Removed 8 rows after 2025-10-22

👤 USER-SPECIFIED DATE FILTER:
   From: 2025-10-10
   To: 2025-10-20

🔍 PART 2: Applying user filter...
   ✓ Removed 23 rows before 2025-10-10
   ✓ Removed 5 rows after 2025-10-20

📊 ACTION_DATE range (after filter):
   Min: 2025-10-10
   Max: 2025-10-20

✅ Date filter complete: 1156 rows remain (91 removed)
```

---

## 📁 Project Structure

```
AMOSFilter/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── run_gui.py                   # GUI launcher
├── AMOSFilter.spec             # PyInstaller build config
│
├── bin/
│   └── link.txt                # Google Drive credentials
│
├── INPUT/                      # Local Excel files (default)
│
├── DATA/                       # Output root folder
│   ├── WP_001/                # Per-file output folders
│   │   └── WP_001_03pm45_27_11_25.xlsx
│   ├── WP_002/
│   ├── temp_gui/              # Temporary downloads
│   └── log/
│       └── logbook_2025_11.xlsx  # Monthly statistics
│
└── doc_validator/             # Main package
    ├── __init__.py
    ├── config.py              # Configuration & paths
    │
    ├── core/                  # Core processing logic
    │   ├── __init__.py
    │   ├── drive_io.py        # Google Drive API
    │   ├── excel_io.py        # Excel I/O operations
    │   ├── excel_pipeline.py  # Validation pipeline
    │   ├── pipeline.py        # High-level orchestration
    │   └── input_source_manager.py  # File source abstraction
    │
    ├── validation/            # Validation engine
    │   ├── __init__.py
    │   ├── constants.py       # Keywords & patterns
    │   ├── patterns.py        # Regex patterns
    │   ├── helpers.py         # Helper functions
    │   └── engine.py          # Main validation logic
    │
    ├── interface/             # GUI & CLI
    │   ├── __init__.py
    │   ├── main_window.py     # PyQt6 main window
    │   ├── cli_main.py        # CLI entry point
    │   │
    │   ├── panels/            # Reusable UI panels
    │   │   ├── __init__.py
    │   │   └── date_filter_panel.py
    │   │
    │   ├── widgets/           # Custom widgets
    │   │   ├── __init__.py
    │   │   └── smart_date_edit.py
    │   │
    │   ├── workers/           # Background threads
    │   │   ├── __init__.py
    │   │   └── processing_worker.py
    │   │
    │   └── styles/            # Theming & styling
    │       ├── __init__.py
    │       └── theme.py       # Dark theme stylesheet
    │
    ├── tools/                 # Utility scripts
    │   ├── __init__.py
    │   ├── process_local_batch.py
    │   └── diagnose_row_loss.py
    │
    └── tests/                 # Test suites
        ├── __init__.py
        ├── test_validators.py
        └── test_real_world_data.py
```

---

## ⚙️ Configuration

### `config.py` Settings

```python
# Base directory (auto-detects source vs EXE mode)
BASE_DIR = Path(__file__).resolve().parent.parent

# Credentials file
LINK_FILE = str(BASE_DIR / "bin" / "link.txt")

# Output folder
DATA_FOLDER = str(BASE_DIR / "DATA")

# Input folder (for local files)
INPUT_FOLDER = str(BASE_DIR / "INPUT")

# Invalid filename characters
INVALID_CHARACTERS = r'[\\/*?:"<>|]'
```

### Google Drive Setup

1. **Get API Key:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Google Drive API
   - Create API key

2. **Get Folder ID:**
   - Open your Google Drive folder
   - Copy ID from URL: `https://drive.google.com/drive/folders/YOUR_FOLDER_ID`

3. **Create `bin/link.txt`:**
   ```
   GG_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXX
   GG_FOLDER_ID=1a2b3c4d5e6f7g8h9i0j
   ```

---

## 🛠️ Development

### Running Tests

**Unit Tests:**
```bash
python -m doc_validator.tests.test_validators
```

**Real-World Data Tests:**
```bash
python -m doc_validator.tests.test_real_world_data
```

### Building EXE (PyInstaller)

```bash
pyinstaller AMOSFilter.spec
```

Output: `EXE/AMOSFilter/AMOSFilter.exe`

### Project Guidelines

**Code Style:**
- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Keep functions under 50 lines

**Module Organization:**
- `core/` - Business logic (no UI code)
- `validation/` - Pure validation functions
- `interface/` - UI code only
- `tools/` - Standalone utility scripts

**Testing:**
- Add tests for new validation rules
- Test edge cases
- Use real-world data samples

---

## 🐛 Troubleshooting

### Common Issues

#### **"No files found in folder"**
**Solution:**
- Check file extensions (.xlsx, .xls)
- Verify folder path is correct
- Ensure files aren't in subfolders

#### **"Drive credentials not configured"**
**Solution:**
- Create `bin/link.txt` with API key and folder ID
- Verify credentials are valid
- Check folder permissions

#### **"Row count mismatch detected"**
**Solution:**
- Check `DATA/WP_XXX/DEBUG/` folder
- Compare input vs output CSV files
- Look for completely empty rows

#### **"All rows filtered out"**
**Solution:**
- Check action_date column format (must be YYYY-MM-DD)
- Verify date range includes valid data
- Check console output for date range info

#### **Progress bar stuck**
**Solution:**
- Check console output for error messages
- Click Cancel and try again
- Check file isn't corrupted

### Debug Mode

Enable detailed logging:
```python
# In excel_pipeline.py
print(f"DEBUG: {row_data}")
```

Check debug CSVs:
```
DATA/WP_XXX/DEBUG/
├── input_original_20251127_153045.csv
└── output_processed_20251127_153045.csv
```

---

## 📊 Changelog

### **v2.0 - Phase 2 (2025-11-27)**
✨ **UI Enhancements:**
- Added dark theme with modern styling
- File details columns (size, modified, status)
- Toggle-style checkboxes
- Gradient progress bar
- Professional fonts and spacing

### **v2.0 - Phase 1 (2025-11-27)**
✨ **Major Features:**
- Multi-threaded processing with progress tracking
- Smart date filtering (2-layer system)
- Collapsible console output
- Refresh button for file list
- Open output folder button
- Real-time progress with cancel option

🔧 **Improvements:**
- Line-count based progress calculation
- Status indicators after processing
- Search bar for filtering files
- Flexible input sources (local/Drive)

### **v1.5 (2025-11-20)**
✨ **Features:**
- PyQt6 GUI with file selection
- Google Drive integration
- Basic validation engine
- Excel output with auto-filter

---

## 📝 License

**Private / Internal Use Only**

This software is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

---

## 👥 Support

For issues, questions, or feature requests:
- Check [Troubleshooting](#-troubleshooting) section
- Review console output logs
- Check `DATA/log/logbook_YYYY_MM.xlsx` for statistics
- Contact development team

---

## 🚀 Future Roadmap

### **Phase 3: Quality-of-Life** (Planned)
- ⚙️ Settings panel (API keys, preferences)
- 💬 Better error dialogs
- 📝 Enhanced logging to file
- 🎨 Light theme option

### **Phase 4+** (Future)
- 📊 Built-in Excel viewer
- 🖱️ Drag-and-drop file support
- 🌐 Web-based version
- 📈 Advanced analytics dashboard

---

**Made with ❤️ for Aviation Maintenance Excellence**

✈️ **AMOSFilter** - Professional Documentation Validation