# AMOSFilter - Documentation Validator

A PyQt6-based desktop application for validating aircraft maintenance documentation references in Excel files from Google Drive.

## Overview

AMOSFilter automates the validation of maintenance documentation references (AMM, SRM, CMM, etc.) in Excel files, ensuring compliance with aviation maintenance standards. It checks for:

- **Reference completeness**: Presence of required documentation references (AMM, SRM, CMM, MEL, etc.)
- **Revision tracking**: Validation of revision dates and numbers
- **Special patterns**: NDT reports, Service Bulletins, Data Module Tasks
- **Date filtering**: Process only records within specified date ranges

## Features

### Core Functionality
- ✅ **Google Drive Integration**: Automatically fetch Excel files from configured Drive folder
- 📊 **Batch Processing**: Process multiple files simultaneously
- 📅 **Smart Date Filtering**: Filter by action date with flexible input formats (YYYY-MM-DD or relative: -1d, +2d, -1m, +1y)
- 🔍 **Multi-State Validation**: Valid, N/A, Missing reference, Missing revision
- 📝 **Automatic Logging**: Monthly logbook with validation statistics
- 🎯 **Smart Auto-Valid Rules**: 
  - SEQ patterns (1.xx, 2.xx, 3.xx, 10.xx)
  - Header keywords (CLOSE UP, JOB SET UP, OPEN/CLOSE ACCESS, GENERAL)

### User Interface
- 🖥️ **Modern GUI**: Clean PyQt6 interface with Fusion style
- ✓ **File Selection**: Checkbox-based multi-file selection
- 📈 **Real-time Progress**: Live console output and progress tracking
- 📁 **Quick Access**: Direct output folder access from GUI
- 🔄 **Refresh**: Manual refresh of Drive file list

### Validation Rules

#### Automatically Valid
- SEQ values: 1.xx, 2.xx, 3.xx, 10.xx
- Headers: CLOSE UP, JOB SET UP, OPEN/CLOSE ACCESS, GENERAL
- Skip phrases: GET ACCESS, GAIN ACCESS, SPARE ORDERED, etc.
- Special patterns: REFERENCED AMM/SRM, NDT REPORT with ID, DATA MODULE TASK + SB

#### Reference Keywords
AMM, DMC, SRM, CMM, EMM, SOPM, SWPM, IPD, FIM, TSM, IPC, SB, AD, NTO, MEL, NEF, MME, LMM, NTM, DWG, AIPC, AMMS, DDG, VSB, BSI, FTD, TIPF, MNT, EEL VNA, EO EOD

#### Revision Indicators
- REV + number (REV 5, REV.10)
- ISSUE + number
- ISSUED SD + number
- TAR + number
- Date-based: EXP DATE, DEADLINE, DUE DATE, REV DATE

## Installation

### Prerequisites
- Python 3.8+
- Google Drive API access
- Windows, macOS, or Linux

### Setup

1. **Clone repository**:
```bash
git clone <repository-url>
cd doc_validator
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure credentials**:
Create `bin/link.txt` with your Google Drive credentials:
```
GG_API_KEY=your_api_key_here
GG_FOLDER_ID=your_folder_id_here
```

4. **Run application**:
```bash
# GUI mode (recommended)
python run_gui.py

# CLI mode (batch processing)
python -m doc_validator.interface.cli_main
```

## Usage

### GUI Mode

1. **Launch application**: `python run_gui.py`
2. **Configure date filter** (optional):
   - Enable checkbox
   - Enter dates as YYYY-MM-DD or relative format (-1d, +2d, -1m, +1y)
3. **Select files**: Check files to process from the list
4. **Run**: Click "▶ Run" button
5. **Monitor progress**: Watch console output and progress bar
6. **Access results**: Click "📁 Open Output Folder" or check `DATA/` directory

### CLI Mode

```bash
# Use default credentials (bin/link.txt)
python -m doc_validator.interface.cli_main

# Use custom credentials file
python -m doc_validator.interface.cli_main path/to/credentials.txt
```

### Local Batch Processing

Process Excel files from a local folder without Google Drive:

```bash
python -m doc_validator.tools.process_local_batch "C:/path/to/excel/files"
```

## Project Structure

```
doc_validator/
├── config.py                      # Application configuration
├── core/
│   ├── drive_io.py               # Google Drive API integration
│   ├── excel_io.py               # Excel file I/O operations
│   ├── excel_pipeline.py         # Main processing pipeline
│   └── pipeline.py               # High-level orchestration
├── interface/
│   ├── main_window.py            # PyQt6 main window
│   ├── panels/
│   │   └── date_filter_panel.py  # Date filter UI component
│   ├── widgets/
│   │   └── smart_date_edit.py    # Smart date input widget
│   └── workers/
│       └── processing_worker.py  # Background processing thread
├── validation/
│   ├── constants.py              # Validation constants
│   ├── patterns.py               # Regex patterns
│   ├── helpers.py                # Validation helpers
│   └── engine.py                 # Core validation logic
└── tools/
    ├── diagnose_row_loss.py      # Row loss diagnostic tool
    └── process_local_batch.py    # Local batch processor
```

## Output

### File Structure
```
DATA/
├── WP_xxx/                        # Work package folders
│   ├── WP_xxx_01pm45_27_11_25.xlsx   # Validated file
│   └── DEBUG/                     # Debug files (if row mismatch)
└── log/
    └── logbook_2025_11.xlsx       # Monthly logbook
```

### Validation Results
Each output Excel file contains:
- All original columns
- **Reason** column with validation result:
  - `Valid`: Complete reference with revision
  - `N/A`: No validation required
  - `Missing reference`: No documentation reference
  - `Missing revision`: Has reference but missing revision date

### Logbook Entries
Monthly Excel logbook tracks:
- Order, DateTime, WP name
- Row counts (original vs output)
- Validation statistics (Valid, N/A, errors)
- SEQ/Header auto-valid counts
- Row mismatch warnings
- Error rate percentage
- Processing time

## Date Filtering

### Format Options

**Absolute dates**:
- `2025-11-27` (YYYY-MM-DD)

**Relative dates**:
- `-1d` (1 day ago)
- `+2d` (2 days from now)
- `-1m` (1 month ago)
- `+1y` (1 year from now)

### Filter Behavior

1. **Auto-filter**: Always applies file's `start_date` and `end_date` columns
2. **User filter**: Optional additional filtering on top of auto-filter
3. **Result**: Rows outside date range are excluded from validation

## Advanced Features

### Smart Date Input Widget
- Single click: Place caret
- Double click: Open calendar popup
- Enter key: Parse and format date
- Supports relative dates with keyboard

### Row Loss Diagnostic
If row count mismatch is detected:
```bash
python -m doc_validator.tools.diagnose_row_loss path/to/file.xlsx
```

### DES Field Context
The validator uses the `DES` column to determine if a reference is expected:
- If DES has references → row without reference = `Missing reference`
- If DES has no references → row without reference = `Valid`

## Configuration

### Customize Validation Rules

Edit `doc_validator/validation/constants.py`:
- `REF_KEYWORDS`: Add/remove reference document types
- `SKIP_PHRASES`: Add procedural phrases to skip
- `HEADER_SKIP_KEYWORDS`: Add header keywords for auto-valid

### Adjust Date Format

Default format: `YYYY-MM-DD` (hard-coded in `excel_pipeline.py`)
To change, modify `format='%Y-%m-%d'` in `apply_date_filter()`

## Dependencies

```
pandas>=2.0.0
openpyxl>=3.1.0
google-api-python-client>=2.0.0
PyQt6>=6.4.0
```

## Building Executable

To create standalone executable with PyInstaller:

```bash
pyinstaller --onedir --windowed --name=AMOSFilter run_gui.py
```

## Troubleshooting

### "No Excel files found"
- Verify Google Drive folder ID is correct
- Check API key permissions
- Ensure files are `.xlsx` or `.xls` format

### "Row count mismatch"
- Check DEBUG folder for input/output comparison CSVs
- Run diagnostic tool: `python -m doc_validator.tools.diagnose_row_loss`
- Verify Excel file format (no merged cells, consistent structure)

### Date filter not working
- Ensure `action_date` column exists in Excel
- Verify date format is YYYY-MM-DD
- Check `start_date`/`end_date` columns in first row

### GUI not launching
- Verify PyQt6 installation: `pip install --upgrade PyQt6`
- Check Python version >= 3.8
- Try running from terminal to see error messages

## License

[Your License Here]

## Contributing

Contributions welcome! Please:
1. Fork repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## Support

For issues or questions:
- Create GitHub issue
- Include error messages and screenshots
- Attach sample Excel file (sanitized)