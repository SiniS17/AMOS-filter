# AMOS Documentation Validator - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [GUI Interface](#gui-interface)
4. [Command Line Interface](#command-line-interface)
5. [Input Files](#input-files)
6. [Output Files](#output-files)
7. [Features](#features)
8. [Common Workflows](#common-workflows)
9. [Tips and Best Practices](#tips-and-best-practices)

---

## Introduction

### What Does This Tool Do?

AMOS Documentation Validator checks aircraft maintenance work orders to ensure that:

1. **References are present** - Each task cites the correct manual (AMM, SRM, CMM, etc.)
2. **Revisions are documented** - Each reference includes a revision number or date
3. **Steps are in order** - (Optional) Work steps are performed in chronological sequence

### Who Is This For?

- Quality Assurance Engineers
- Maintenance Planners
- Documentation Specialists
- Compliance Officers
- Aircraft Maintenance Teams

### What You'll Need

- Excel files containing work order data (`.xlsx` or `.xls`)
- Python 3.8+ installed
- (Optional) Google Drive API credentials for cloud processing

---

## Getting Started

### First Time Setup

1. **Install the application**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-gui.txt  # For GUI
   ```

2. **Prepare your input folder**
   - Create a folder named `INPUT` in the application directory
   - Place your Excel files there

3. **Run the application**
   ```bash
   python run_gui.py
   ```

### Quick Test

Try the validator with a sample file:

```bash
python -m doc_validator.tools.process_local_batch ./INPUT
```

---

## GUI Interface

### Main Window Overview

```
┌─────────────────────────────────────────────────────┐
│  AMOS Document Validators              BETA v1.25   │
├──────────────┬──────────────────────────────────────┤
│              │  Input Files          🔍 [Search]    │
│  Input       │  ┌──────────────────────────────────┐│
│  Source      │  │☐ file1.xlsx    📁Local  2.1MB   ││
│              │  │☐ file2.xlsx    📁Local  1.8MB   ││
│  Date Filter │  │☑ file3.xlsx    ☁️Drive   3.2MB   ││
│  (Optional)  │  └──────────────────────────────────┘│
│              │  [✓ Select All] [✗ Deselect All]    │
│  Action Step │  [▶ Run Processing]                  │
│  Control     │                                       │
│              │  📝 Console Output                    │
│  [Open       │  ┌──────────────────────────────────┐│
│   Output]    │  │ Processing file1.xlsx...         ││
│              │  │ ✓ Validation complete            ││
└──────────────┴──────────────────────────────────────┘
```

### Step-by-Step Guide

#### 1. Choose Input Source

**Local Folder (Default)**
- Click **"📁 Browse..."** to select a folder
- All `.xlsx` and `.xls` files will be listed
- Default location: `./INPUT` folder

**Google Drive**
- Select **"☁️ Google Drive"** from dropdown
- Requires `bin/link.txt` with credentials
- Files are listed automatically

#### 2. Select Files

- **Check boxes** next to files you want to process
- Use **"✓ Select All"** to select everything
- Use **"✗ Deselect All"** to clear selection
- **Search bar** filters files by name

#### 3. Configure Options

**Date Filter (Optional)**
- Check **"Enable date filtering"**
- Set date range:
  - **From**: Start date (inclusive)
  - **To**: End date (inclusive)
- Supports formats:
  - Absolute: `2024-01-15`
  - Relative: `-30d` (30 days ago), `+1m` (1 month from last date)

**Action Step Control**
- Check **"Run Action Step Control (ASC)"** to verify step order
- Uncheck to skip chronological verification
- Recommended: Keep enabled unless processing very old data

#### 4. Run Processing

- Click **"▶ Run Processing"**
- Watch progress in console output
- Progress bar shows current status
- Each file shows: ✓ Success or ✗ Failed

#### 5. View Results

- Click **"📂 Open Output"** to view processed files
- Output files are in `DATA/<WorkPackage>/` folders
- Check console for detailed statistics

### GUI Features Explained

#### Search Bar
Type to filter the file list in real-time:
```
Search: "787"  →  Shows only files with "787" in name
Search: "jan"  →  Shows only files with "jan" in name
```

#### Status Column
Shows processing result:
- **Empty** - Not yet processed
- **✓ Success** - Processed successfully
- **✗ Failed** - Processing failed (check console)

#### Console Output
Real-time processing log:
```
Processing file: WP_123_RAW.xlsx
✓ Read 450 rows, 15 columns
✓ 420 rows after date filtering
✓ Validation complete
  ✅ Valid: 380
  ❌ Missing reference: 25
  ❌ Missing revision: 15
✓ File saved: WP_123_10am15_21_12_24.xlsx
```

#### Refresh Button (Header Icon)
- Click the refresh icon in the table header to reload the file list
- Useful after adding new files to the input folder

---

## Command Line Interface

### Basic Usage

```bash
# Use default credentials (bin/link.txt)
python -m doc_validator.interface.cli_main

# Use custom credentials file
python -m doc_validator.interface.cli_main /path/to/credentials.txt

# Disable Action Step Control
python -m doc_validator.interface.cli_main --no-asc
```

### Batch Processing Local Files

```bash
# Process all Excel files in a folder
python -m doc_validator.tools.process_local_batch ./INPUT

# With ASC disabled
python -m doc_validator.tools.process_local_batch ./INPUT --no-asc
```

### CLI Output

```
==============================================================
Documentation Validator - BATCH MODE
==============================================================

Using default credentials file from config: bin/link.txt
Authenticating with Google Drive API...
✓ Authentication successful
Listing and downloading Excel files from folder...

📁 Found 3 Excel file(s) in folder:
   1. WP_123_RAW.xlsx
   2. WP_456_RAW.xlsx
   3. WP_789_RAW.xlsx

📥 Downloading 3 file(s)...

[1/3] Downloading: WP_123_RAW.xlsx
   ✓ Downloaded to: DATA/temp_download/WP_123_RAW.xlsx

...

==============================================================
BATCH PROCESSING COMPLETE
==============================================================

📊 Summary:
   Total files: 3
   ✅ Successful: 3
   ❌ Failed: 0

✅ Successfully processed files:
   1. WP_123_RAW.xlsx
      → DATA/WP_123/WP_123_10am15_21_12_24.xlsx
```

---

## Input Files

### Required Columns

Your Excel file must contain these columns (case-insensitive):

| Column Name | Description | Example |
|-------------|-------------|---------|
| `WO` | Work Order number | `7123456` |
| `wo_text_action.text` | Action description | `IAW AMM 52-11-01 REV 156` |
| `SEQ` | Sequence number | `4.1` |
| `Workstep` | Work step number | `1` |
| `action_date` | Date performed | `2024-01-15` |

### Optional Columns

| Column Name | Purpose |
|-------------|---------|
| `wo_text_action.header` | Step header (for skip detection) |
| `DES` | Description/context field |
| `WP` | Work Package identifier |
| `action_time` | Time performed (for ASC) |
| `start_date` | File date range start |
| `end_date` | File date range end |

### File Format Requirements

- **File type**: `.xlsx` or `.xls`
- **Header row**: Row 1 must contain column names
- **Encoding**: UTF-8 recommended
- **Date format**: `YYYY-MM-DD` (e.g., `2024-01-15`)
- **Size limit**: No hard limit, but >100MB may be slow

### Sample Input

```
WO       | SEQ | Workstep | wo_text_action.text                | action_date
---------|-----|----------|-----------------------------------|------------
7123456  | 4.1 | 1        | IAW AMM 52-11-01 REV 156          | 2024-01-15
7123456  | 4.1 | 2        | REMOVED PANEL                      | 2024-01-15
7123456  | 4.1 | 3        | REF SRM 54-21-03 ISSUE 002        | 2024-01-16
```

---

## Output Files

### Main Output File

**Location**: `DATA/<WorkPackage>/WP_<WorkPackage>_<timestamp>.xlsx`

**Example**: `DATA/WP_123/WP_123_10am15_21_12_24.xlsx`

#### Sheet 1: "REF REV" (Main Results)

Contains validation results with these columns:

| Column | Description |
|--------|-------------|
| `WO` | Work Order number |
| `WO_state` | Work Order state |
| `SEQ` | Sequence number |
| `Workstep` | Work step number |
| `DES` | Description |
| `wo_text_action.header` | Step header |
| `wo_text_action.text` | Action text |
| `action_date` | Date performed |
| `wo_text_action.sign_performed` | Signature |
| **`Reason`** | **Validation result** |

**Reason Values**:
- `Valid` ✅ - Correct reference and revision
- `Missing reference` ❌ - No reference found
- `Missing revision` ❌ - Reference without revision
- `N/A` ⚪ - Blank or N/A entry
- *(Empty)* - Auto-valid (SEQ 1.x, 2.x, 3.x, 10.x or header keywords)

#### Sheet 2: "ActionStepControl" (Optional)

If Action Step Control is enabled, contains:

| Column | Description |
|--------|-------------|
| *All columns from REF REV* | Same as main sheet |
| `ActionStepOrderOK` | `TRUE` or `FALSE` |
| `ActionStepIssue` | Description of timing issue |

#### Sheet 3: "ASC_Summary" (Optional)

Summary by Work Order:

| Column | Description |
|--------|-------------|
| `wo` | Work Order number |
| `num_worksteps` | Total work steps |
| `status` | OK or VIOLATIONS |
| `num_violations` | Count of order violations |

### Logbook

**Location**: `DATA/log/logbook_YYYY_MM.xlsx`

**Example**: `DATA/log/logbook_2024_12.xlsx`

Monthly logbook tracking all processing runs:

| Column | Description |
|--------|-------------|
| `Order` | Run number |
| `DateTime` | When processed |
| `WP` | Work Package |
| `Orig rows` | Input row count |
| `Out rows` | Output row count |
| `Valid` | Count of valid rows |
| `N/A` | Count of N/A rows |
| `Missing reference` | Count |
| `Missing revision` | Count |
| `SEQ auto-valid` | Count of auto-valid SEQ |
| `Row mismatch` | TRUE if rows lost |
| `Total errors` | Sum of errors |
| `Error rate (%)` | Percentage |
| `Processing time (s)` | Duration |

---

## Features

### 1. Reference Validation

Checks for proper documentation references:

**Supported Reference Types**:
- AMM (Aircraft Maintenance Manual)
- SRM (Structural Repair Manual)
- CMM (Component Maintenance Manual)
- EMM (Engine Maintenance Manual)
- MEL (Minimum Equipment List)
- NEF (Non-Essential Function)
- SB (Service Bulletin)
- NDT (Non-Destructive Testing)
- And 20+ more types

**Validation Logic**:
1. Checks for reference keyword (AMM, SRM, etc.)
2. Verifies revision indicator (REV, ISSUE, EXP, DEADLINE)
3. Handles special patterns (NDT REPORT, SB full numbers)
4. Auto-corrects common typos

**Example Valid Entries**:
```
✅ IAW AMM 52-11-01 REV 156
✅ REF SRM 54-21-03 ISSUE 002
✅ PER CMM 32-42-11 REV. 45
✅ REF NDT REPORT NDT02-251067
✅ IAW SB B787-A-21-00-0128-02A-933B-D
✅ DATA MODULE TASK 2, SB B787-A-21-00-0128
```

### 2. Auto-Valid Sequences

Certain SEQ values are automatically marked as Valid:

- **SEQ 1.x** - Initial setup tasks
- **SEQ 2.x** - Preparation tasks
- **SEQ 3.x** - Access tasks
- **SEQ 10.x** - Closeup tasks

**Rationale**: These are procedural steps that don't require specific documentation references.

### 3. Header Keywords

Tasks with these headers are automatically Valid:

- CLOSE UP
- JOB SET UP
- OPEN ACCESS
- CLOSE ACCESS
- GENERAL

**Rationale**: Setup and closeup tasks are procedural.

### 4. Skip Phrases

Text containing these phrases is marked Valid:

- GET ACCESS / GAIN ACCESS
- SPARE ORDERED
- REFER RESULT WT (work task cross-reference)
- WO: (work order cross-reference)

### 5. Date Filtering

Filter work orders by `action_date`:

**Two-Stage Filtering**:

1. **Automatic** - Uses file's `start_date` and `end_date` columns
2. **User Override** - Optional date range you specify

**Date Format Support**:
- Absolute: `2024-01-15`
- Relative (from last valid date):
  - `-30d` (30 days ago)
  - `+1m` (1 month forward)
  - `-1y` (1 year ago)

**Example**:
```
File range: 2024-01-01 to 2024-12-31
User filter: 2024-06-01 to 2024-08-31
Result: Only June-August data processed
```

### 6. Action Step Control

Verifies chronological order of maintenance steps within each Work Order.

**What It Checks**:
- Each work step has a valid timestamp
- Steps are performed in logical order
- Later steps don't precede earlier steps

**Output**:
- `ActionStepOrderOK`: TRUE/FALSE
- `ActionStepIssue`: Description if FALSE

**Example Issue**:
```
Work Order: 7123456
  Step 1: 2024-01-15 10:00 ✅ OK
  Step 2: 2024-01-15 11:00 ✅ OK
  Step 3: 2024-01-15 09:00 ❌ Earlier than steps 1, 2
```

### 7. Typo Auto-Correction

Common typos are automatically fixed:

| Before | After |
|--------|-------|
| `REFAMM` | `REF AMM` |
| `REV156` | `REV 156` |
| `AMM52-11-01` | `AMM 52-11-01` |
| `REV:156` | `REV 156` |

---

## Common Workflows

### Workflow 1: Daily Quality Check

**Goal**: Check today's work orders

1. Export today's work orders from AMOS to Excel
2. Save to `INPUT` folder
3. Run GUI → Select file → Run
4. Review results for errors
5. Export error list for correction

### Workflow 2: Monthly Audit

**Goal**: Validate all work orders for the month

1. Export monthly data from AMOS
2. Use date filter: `2024-11-01` to `2024-11-30`
3. Run batch processing
4. Generate report from logbook
5. Send to management

### Workflow 3: Historical Data Cleanup

**Goal**: Validate old work orders

1. Collect historical Excel files
2. Disable Action Step Control (old data may lack timestamps)
3. Process batch with `--no-asc` flag
4. Review and correct errors
5. Re-import to AMOS

### Workflow 4: Pre-Audit Preparation

**Goal**: Ensure all documentation is compliant before audit

1. Export all active work packages
2. Process with ASC enabled
3. Generate error report
4. Assign corrections to team
5. Re-validate after corrections
6. Present clean logbook to auditors

---

## Tips and Best Practices

### Data Quality

1. **Clean your data first**
   - Remove completely blank rows
   - Ensure dates are in YYYY-MM-DD format
   - Check for merged cells (unsupported)

2. **Use consistent naming**
   - Work package codes should be consistent
   - File names should include WP identifier

3. **Test with small samples**
   - Process 1-2 files first to verify
   - Check output format matches expectations

### Performance

1. **Batch size**
   - Process 10-20 files at a time for optimal performance
   - Very large files (>50MB) may take several minutes

2. **Date filtering**
   - Use date filters to reduce processing time
   - Narrower date ranges = faster processing

3. **Action Step Control**
   - Disable for historical data without timestamps
   - Disable if you only need reference validation

### Quality Assurance

1. **Review logbook regularly**
   - Check error rates
   - Identify patterns in missing references
   - Track improvement over time

2. **Spot-check results**
   - Randomly verify 5-10 "Valid" entries
   - Check "Missing reference" entries manually
   - Ensure false positives are minimal

3. **Maintain documentation**
   - Keep record of processing dates
   - Document any manual corrections
   - Update validation rules if needed

### Troubleshooting

1. **Row count mismatch**
   - Check console for "LOST ROWS" warning
   - Review DEBUG folder for comparison files
   - Report to developer if persistent

2. **Unexpected validation results**
   - Check for typos in reference text
   - Verify column names match expected format
   - Review validation rules documentation

3. **Google Drive issues**
   - Verify API key is valid
   - Check folder ID is correct
   - Ensure API is enabled in Google Cloud

---

## Keyboard Shortcuts (GUI)

| Shortcut | Action |
|----------|--------|
| `Ctrl+A` | Select all files |
| `Ctrl+D` | Deselect all files |
| `Ctrl+F` | Focus search bar |
| `Enter` (in search) | Clear and refocus |
| `Double-click date` | Open calendar picker |

---

## Getting Help

- **Documentation**: Check other docs in `docs/` folder
- **Issues**: Report bugs on GitHub Issues
- **Questions**: Use GitHub Discussions
- **Updates**: Check CHANGELOG.md for new features

---

**Next Steps**:
- Review [Validation Rules](VALIDATION_RULES.md) for complete logic
- See [Troubleshooting](TROUBLESHOOTING.md) for common issues
- Check [API Reference](API_REFERENCE.md) for programmatic use