# Configuration Guide

Complete guide to configuring AMOS Documentation Validator.

## Table of Contents

- [Overview](#overview)
- [File Locations](#file-locations)
- [Configuration Files](#configuration-files)
- [Validation Settings](#validation-settings)
- [Google Drive Setup](#google-drive-setup)
- [Advanced Configuration](#advanced-configuration)

---

## Overview

AMOS Validator can be configured through:
1. **Configuration files** - Python modules with settings
2. **Credentials files** - API keys and folder IDs
3. **Command-line arguments** - Runtime options
4. **GUI settings** - User interface options

---

## File Locations

### Project Structure

```
amos-validator/
├── bin/
│   └── link.txt              # Google Drive credentials
├── DATA/                     # Output folder (auto-created)
│   ├── <WP>/                # Per work package folders
│   └── log/                 # Monthly logbooks
├── INPUT/                    # Local input folder (auto-created)
├── doc_validator/
│   ├── config.py            # Main configuration
│   └── validation/
│       └── constants.py      # Validation settings
└── requirements.txt          # Dependencies
```

### Configuration Modules

| File | Purpose | User Editable |
|------|---------|---------------|
| `doc_validator/config.py` | Global settings | ✅ Yes |
| `doc_validator/validation/constants.py` | Validation rules | ✅ Yes |
| `bin/link.txt` | Drive credentials | ✅ Yes |
| `doc_validator/validation/patterns.py` | Regex patterns | ⚠️ Advanced |
| `doc_validator/validation/helpers.py` | Helper functions | ⚠️ Advanced |

---

## Configuration Files

### doc_validator/config.py

Main configuration file with paths and global settings.

```
python
from pathlib import Path
import sys

# Base directory detection
if getattr(sys, 'frozen', False):
    # Running as executable
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    # Running as Python script
    BASE_DIR = Path(__file__).resolve().parent.parent

# Credentials file
LINK_FILE = str(BASE_DIR / "bin" / "link.txt")

# Output folders
DATA_FOLDER = str(BASE_DIR / "DATA")
INPUT_FOLDER = str(BASE_DIR / "INPUT")
LOG_FOLDER = "log"

# Invalid filename characters
INVALID_CHARACTERS = r'[\\/*?:"<>|]'

# Action Step Control settings
ACTION_STEP_CONTROL_ENABLED_DEFAULT = True
ACTION_STEP_SHEET_NAME = "ActionStepControl"
ACTION_STEP_SUMMARY_ENABLED_DEFAULT = True
ACTION_STEP_SUMMARY_SHEET_NAME = "ASC_Summary"
```

#### Customizable Settings

**Change output folder**:
```
python
# Default
DATA_FOLDER = str(BASE_DIR / "DATA")

# Custom location
DATA_FOLDER = "C:/MyOutputFolder"
# Or
DATA_FOLDER = "/home/user/outputs"
```

**Change input folder**:
```
python
# Default
INPUT_FOLDER = str(BASE_DIR / "INPUT")

# Custom location
INPUT_FOLDER = "C:/MyExcelFiles"
```

**Disable Action Step Control by default**:
```
python
ACTION_STEP_CONTROL_ENABLED_DEFAULT = False
```

**Change sheet names**:
```
python
ACTION_STEP_SHEET_NAME = "TimeValidation"
ACTION_STEP_SUMMARY_SHEET_NAME = "Summary"
```

---

### doc_validator/validation/constants.py

Validation rules and keywords.

```
python
# Reference keywords (document types)
REF_KEYWORDS = [
    "AMM", "DMC", "SRM", "CMM", "EMM", "SOPM", "SWPM",
    "IPD", "FIM", "TSM", "IPC", "SB", "AD",
    "NTO", "MEL", "NEF", "MME", "LMM", "NTM", "DWG", 
    "AIPC", "AMMS", "DDG", "VSB", "BSI", "FIM", "FTD", 
    "TIPF", "MNT", "EEL VNA", "EO EOD", "NDT Manual"
]

# Linking keywords (IAW, REF, PER)
IAW_KEYWORDS = ["IAW", "REF", "PER", "I.A.W"]

# Skip phrases (automatically valid)
SKIP_PHRASES = [
    "GET ACCESS", "GAIN ACCESS", "GAINED ACCESS", 
    "ACCESS GAINED", "SPARE ORDERED", "ORDERED SPARE",
    "OBEY ALL", "FOLLOW ALL", "COMPLY WITH", 
    "MEASURE AND RECORD", "SET TO INACTIVE", 
    "SEE FIGURE", "REFER TO FIGURE"
]

# Header skip keywords (automatically valid)
HEADER_SKIP_KEYWORDS = [
    "CLOSE UP", "CLOSEUP", "JOB SET UP", "JOB SETUP", 
    "JOBSETUP", "CLOSE-UP", "CLOSE-UP:", "JOP SET-UP",
    "OPEN ACCESS", "OPENACCESS", "JOB SET-UP 1 - GENERAL",
    "CLOSE ACCESS", "CLOSEACCESS", "GENERAL", 
    "JOB SET-UP", "JOB CLOSE-UP"
]

# Invalid characters for folder names
INVALID_CHARACTERS = r'[\\/:*?"<>|]'
```

#### Customization Examples

**Add custom document type**:
```
python
REF_KEYWORDS = [
    "AMM", "SRM", "CMM",
    # ... existing keywords ...
    "CUSTOM_DOC",  # Your custom type
]
```

**Add custom skip phrase**:
```
python
SKIP_PHRASES = [
    "GET ACCESS", "SPARE ORDERED",
    # ... existing phrases ...
    "MY CUSTOM PHRASE",
]
```

**Add custom header keyword**:
```
python
HEADER_SKIP_KEYWORDS = [
    "CLOSE UP", "JOB SET UP",
    # ... existing keywords ...
    "MY SETUP TASK",
]
```

**Remove a keyword** (not recommended):
```
python
# Remove "DMC" from reference keywords
REF_KEYWORDS = [k for k in REF_KEYWORDS if k != "DMC"]
```

---

## Validation Settings

### SEQ Auto-Valid Patterns

Currently hard-coded in `helpers.py`:

```
python
def is_seq_auto_valid(seq_value):
    """Check if SEQ is auto-valid (1.x, 2.x, 3.x, 10.x)"""
    seq_str = str(seq_value).strip()
    return (
        seq_str.startswith("1.") or
        seq_str.startswith("2.") or
        seq_str.startswith("3.") or
        seq_str.startswith("10.")
    )
```

**To customize** (add to `constants.py`):
```
python
# Add this to constants.py
SEQ_AUTO_VALID_PATTERNS = ["1.", "2.", "3.", "10.", "99."]

# Then modify helpers.py to use this list
def is_seq_auto_valid(seq_value):
    from doc_validator.validation.constants import SEQ_AUTO_VALID_PATTERNS
    seq_str = str(seq_value).strip()
    return any(seq_str.startswith(p) for p in SEQ_AUTO_VALID_PATTERNS)
```

### Revision Patterns

Defined in `patterns.py`:

```
python
# Standard revision formats
REV_PATTERN = re.compile(r'\bREV\s*[:\.]?\s*\d+\b', re.IGNORECASE)
ISSUE_PATTERN = re.compile(r'\bISSUE\s*[:\.]?\s*\d+\b', re.IGNORECASE)

# Date-based revisions
EXP_DATE_PATTERN = re.compile(
    r'\b(?:EXP|DEADLINE)\s*[:\.]?\s*\d{1,2}[-/]?[A-Z]{3}[-/]?\d{2,4}\b',
    re.IGNORECASE
)
```

**To add custom revision pattern**:
```
python
# Add to patterns.py
MY_REV_PATTERN = re.compile(r'\bMYREV\s*\d+\b', re.IGNORECASE)

# Add to has_revision() in helpers.py
def has_revision(text: str) -> bool:
    # ... existing checks ...
    if MY_REV_PATTERN.search(text):
        return True
    return False
```

---

## Google Drive Setup

### bin/link.txt Format

```
GG_API_KEY=your_api_key_here
GG_FOLDER_ID=your_folder_id_here
```

### Getting API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project
3. Enable Google Drive API
4. Create API Key
5. Copy key to `link.txt`

### Getting Folder ID

1. Open folder in Google Drive
2. Copy ID from URL:
   ```
   https://drive.google.com/drive/folders/1ABCdefGHIjkl
                                           └── This is the Folder ID
   ```

### Security Best Practices

**Restrict API Key**:
1. Go to API Key settings
2. Under "API restrictions":
   - Select "Restrict key"
   - Choose "Google Drive API"
3. Under "Application restrictions":
   - Select "IP addresses" (for server deployment)
   - Or "HTTP referrers" (for web apps)

**Rotate keys regularly**:
```bash
# Generate new key
# Update bin/link.txt
# Delete old key from Google Cloud
```

**Never commit credentials**:
```bash
# Ensure .gitignore includes:
bin/link.txt
*.txt
```

---

## Advanced Configuration

### Output File Format

Edit `excel_io.py` to customize output columns:

```
python
# In write_output_excel()
output_columns = [
    "WO",
    "WO_state",
    "SEQ",
    "Workstep",
    "DES",
    "wo_text_action.header",
    "wo_text_action.text",
    "action_date",
    "wo_text_action.sign_performed",
    "Reason",
    # Add your custom columns here
]
```

### Logbook Format

Edit `excel_io.py` `append_to_logbook()` to customize logbook columns:

```
python
row = {
    "Order": None,
    "DateTime": now.strftime("%Y-%m-%d %H:%M:%S"),
    "WP": wp_value,
    # ... existing columns ...
    "MyCustomField": my_value,  # Add custom field
}
```

### Date Format

Currently hard-coded as `YYYY-MM-DD`. To change:

1. Edit `excel_pipeline.py` `apply_date_filter()`:
```
python
# Current
df[action_date_col] = pd.to_datetime(
    df[action_date_col],
    format='%Y-%m-%d',  # Change this
    errors='coerce'
)
```

2. Update output format:
```
python
# Current
df[action_date_col] = df[action_date_col].dt.strftime('%Y-%m-%d')

# Custom
df[action_date_col] = df[action_date_col].dt.strftime('%d/%m/%Y')
```

### Timeout Settings

For Google Drive downloads, edit `drive_io.py`:

```
python
# Add timeout to requests
import socket
socket.setdefaulttimeout(300)  # 5 minutes

# Or in download function
downloader = MediaIoBaseDownload(fh, request, chunksize=1024*1024)
```

### Memory Management

For large files, edit `excel_io.py`:

```
python
# Read in chunks
def read_input_excel_chunked(file_path: str, chunksize: int = 10000):
    """Read Excel in chunks for large files"""
    chunks = []
    for chunk in pd.read_excel(
        file_path,
        engine='openpyxl',
        chunksize=chunksize,
        # ... other settings ...
    ):
        chunks.append(chunk)
    return pd.concat(chunks, ignore_index=True)
```

---

## Environment Variables

You can use environment variables for configuration:

```
python
# In config.py
import os

# Use environment variable if set, otherwise use default
DATA_FOLDER = os.getenv('AMOS_DATA_FOLDER', str(BASE_DIR / "DATA"))
INPUT_FOLDER = os.getenv('AMOS_INPUT_FOLDER', str(BASE_DIR / "INPUT"))
```

**Usage**:
```bash
# Linux/macOS
export AMOS_DATA_FOLDER="/my/custom/path"
python run_gui.py

# Windows
set AMOS_DATA_FOLDER=C:\My\Custom\Path
python run_gui.py
```

---

## Configuration Validation

### Verify Configuration

Create `verify_config.py`:

```
python
#!/usr/bin/env python3
"""Verify configuration is correct."""

from doc_validator.config import *
from doc_validator.validation.constants import *
import os

def verify_config():
    print("Verifying configuration...")
    
    # Check folders exist or can be created
    for folder in [DATA_FOLDER, INPUT_FOLDER]:
        os.makedirs(folder, exist_ok=True)
        print(f"✓ {folder}")
    
    # Check credentials file
    if os.path.exists(LINK_FILE):
        print(f"✓ Credentials file: {LINK_FILE}")
    else:
        print(f"⚠️  Credentials file not found: {LINK_FILE}")
    
    # Check validation keywords
    print(f"✓ {len(REF_KEYWORDS)} reference keywords")
    print(f"✓ {len(SKIP_PHRASES)} skip phrases")
    print(f"✓ {len(HEADER_SKIP_KEYWORDS)} header keywords")
    
    print("\nConfiguration OK!")

if __name__ == "__main__":
    verify_config()
```

**Run**:
```bash
python verify_config.py
```

---

## Configuration Templates

### Minimal Configuration

For basic validation only:

```
python
# config.py - minimal
BASE_DIR = Path(__file__).parent.parent
DATA_FOLDER = str(BASE_DIR / "DATA")
INPUT_FOLDER = str(BASE_DIR / "INPUT")
ACTION_STEP_CONTROL_ENABLED_DEFAULT = False

# constants.py - minimal
REF_KEYWORDS = ["AMM", "SRM", "CMM"]
IAW_KEYWORDS = ["IAW", "REF"]
SKIP_PHRASES = []
HEADER_SKIP_KEYWORDS = []
```

### Maximum Validation

For strictest validation:

```
python
# config.py - strict
ACTION_STEP_CONTROL_ENABLED_DEFAULT = True

# constants.py - strict (use all defaults)
# Remove all skip phrases to enforce references everywhere
SKIP_PHRASES = []  
HEADER_SKIP_KEYWORDS = []
```

### Production Configuration

For server deployment:

```
python
# config.py - production
import os

BASE_DIR = Path("/opt/amos-validator")
DATA_FOLDER = "/mnt/storage/amos_data"
INPUT_FOLDER = "/mnt/storage/amos_input"
LINK_FILE = os.getenv('AMOS_CREDENTIALS_FILE')

# Enable all features
ACTION_STEP_CONTROL_ENABLED_DEFAULT = True
```

---

## Testing Configuration

After making changes:

```bash
# Run tests
python -m doc_validator.tests.test_validators

# Test with sample file
python -m doc_validator.tools.process_local_batch ./INPUT

# Verify output
ls -la DATA/
```

---

## Troubleshooting Configuration

### Problem: Changes not taking effect

**Solution**:
1. Restart Python/application
2. Clear `__pycache__`:
   ```bash
   find . -type d -name __pycache__ -exec rm -rf {} +
   ```
3. Reinstall in development mode:
   ```bash
   pip install -e .
   ```

### Problem: Import errors after changes

**Solution**:
1. Check syntax errors
2. Ensure imports are correct
3. Run linter:
   ```bash
   flake8 doc_validator/
   ```

---

## See Also

- [User Guide](USER_GUIDE.md) - How to use the validator
- [Developer Guide](DEVELOPER_GUIDE.md) - Development information
- [Validation Rules](VALIDATION_RULES.md) - Validation logic
- [API Reference](API_REFERENCE.md) - Function documentation