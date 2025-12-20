# API Reference

Complete API documentation for AMOS Documentation Validator modules and functions.

## Table of Contents

- [Core Modules](#core-modules)
- [Validation Module](#validation-module)
- [Tools Module](#tools-module)
- [Interface Module](#interface-module)
- [Configuration](#configuration)

---

## Core Modules

### doc_validator.core.excel_pipeline

Main processing pipeline for Excel files.

#### `process_excel()`

```
python
def process_excel(
    file_path: str,
    filter_start_date: Optional[date] = None,
    filter_end_date: Optional[date] = None,
    enable_action_step_control: bool = True
) -> Optional[str]:
    """
    Process Excel file with validation and optional date filtering.
    
    Args:
        file_path: Path to input Excel file (.xlsx or .xls)
        filter_start_date: Optional start date (inclusive) for filtering
        filter_end_date: Optional end date (inclusive) for filtering
        enable_action_step_control: Whether to run Action Step Control
        
    Returns:
        Path to output Excel file if successful, None if error
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If file format is invalid
        
    Example:
        >>> output = process_excel("input.xlsx")
        >>> print(f"Processed: {output}")
        Processed: DATA/WP_123/WP_123_10am15_21_12_24.xlsx
        
        >>> from datetime import date
        >>> output = process_excel(
        ...     "input.xlsx",
        ...     filter_start_date=date(2024, 1, 1),
        ...     filter_end_date=date(2024, 12, 31)
        ... )
    """
```

#### `apply_date_filter()`

```
python
def apply_date_filter(
    df: pd.DataFrame,
    filter_start_date: Optional[date] = None,
    filter_end_date: Optional[date] = None
) -> pd.DataFrame:
    """
    Apply date filtering to DataFrame.
    
    Two-stage filtering:
    1. Auto-filter by file's start_date and end_date columns
    2. User-specified filter (if provided)
    
    Args:
        df: Input DataFrame with action_date column
        filter_start_date: Optional user start date
        filter_end_date: Optional user end date
        
    Returns:
        Filtered DataFrame
        
    Note:
        Removes rows with invalid date formats
        Expects action_date in YYYY-MM-DD format
    """
```

### doc_validator.core.excel_io

Excel file I/O operations.

#### `read_input_excel()`

```
python
def read_input_excel(file_path: str) -> pd.DataFrame:
    """
    Read Excel file with strict settings to avoid data loss.
    
    Args:
        file_path: Path to Excel file
        
    Returns:
        DataFrame with all data as strings
        
    Settings:
        - engine: openpyxl
        - header: Row 0
        - keep_default_na: False (preserves "N/A")
        - dtype: str (all columns as strings)
        - na_filter: False (prevents auto-conversion)
    """
```

#### `write_output_excel()`

```
python
def write_output_excel(
    df: pd.DataFrame,
    output_file: str,
    extra_sheets: Optional[Dict[str, pd.DataFrame]] = None
) -> None:
    """
    Write processed DataFrame to Excel with multiple sheets.
    
    Args:
        df: Main DataFrame to write
        output_file: Path to output file
        extra_sheets: Optional dict of {sheet_name: DataFrame}
        
    Output Format:
        Sheet 1: "REF REV" - Filtered validation results
        Sheet 2+: Additional sheets from extra_sheets dict
        
    Features:
        - Auto-filter enabled on all sheets
        - Preserves column order
        - Formats as Excel table
        
    Example:
        >>> write_output_excel(
        ...     df,
        ...     "output.xlsx",
        ...     extra_sheets={"ActionStepControl": asc_df}
        ... )
    """
```

#### `append_to_logbook()`

```
python
def append_to_logbook(
    wp_value: str,
    counts: Dict[str, int],
    processing_time: Optional[float] = None
) -> None:
    """
    Append processing run to monthly logbook.
    
    Args:
        wp_value: Work Package identifier
        counts: Dict with validation counts:
            - orig_rows: Original row count
            - out_rows: Output row count
            - Valid: Count of valid rows
            - N/A: Count of N/A rows
            - Missing reference: Count
            - Missing revision: Count
            - seq_auto_valid: Count of SEQ auto-valid
        processing_time: Duration in seconds
        
    Output:
        Creates/updates DATA/log/logbook_YYYY_MM.xlsx
        
    Logbook Columns:
        - Order: Sequential run number
        - DateTime: Timestamp
        - WP: Work Package
        - Orig rows, Out rows
        - Valid, N/A, Missing reference, Missing revision
        - SEQ auto-valid
        - Row mismatch: Boolean
        - Total errors: Sum of errors
        - Error rate (%): Percentage
        - Processing time (s): Duration
    """
```

### doc_validator.core.drive_io

Google Drive integration.

#### `authenticate_drive_api()`

```
python
def authenticate_drive_api(api_key: str):
    """
    Authenticate with Google Drive API using API key.
    
    Args:
        api_key: Google Drive API key (GG_API_KEY)
        
    Returns:
        Authenticated Google Drive service object
        
    Raises:
        Exception: If authentication fails
        
    Example:
        >>> service = authenticate_drive_api("AIzaSyB...")
        >>> # Use service to access Drive
    """
```

#### `get_all_excel_files_from_folder()`

```
python
def get_all_excel_files_from_folder(
    drive_service,
    folder_id: str
) -> List[Dict[str, str]]:
    """
    Get all Excel files from Google Drive folder.
    
    Args:
        drive_service: Authenticated Drive service
        folder_id: Google Drive folder ID
        
    Returns:
        List of file info dicts:
        [
            {
                "id": "1ABC...",
                "name": "file.xlsx",
                "mimeType": "application/vnd..."
            },
            ...
        ]
        
    Note:
        Filters by .xlsx and .xls extensions
        Returns empty list if no files found
    """
```

#### `download_file_from_drive()`

```
python
def download_file_from_drive(
    drive_service,
    file_id: str,
    wp_value: str,
    file_name: Optional[str] = None
) -> Optional[str]:
    """
    Download single file from Google Drive.
    
    Args:
        drive_service: Authenticated Drive service
        file_id: Google Drive file ID
        wp_value: Work package for folder naming
        file_name: Optional custom filename
        
    Returns:
        Local file path if successful, None on error
        
    Output Location:
        DATA/<wp_value>/<file_name>
        
    Example:
        >>> path = download_file_from_drive(
        ...     service,
        ...     "1ABC...",
        ...     "WP_123",
        ...     "input.xlsx"
        ... )
        >>> print(path)
        DATA/WP_123/input.xlsx
    """
```

### doc_validator.core.pipeline

High-level processing pipeline.

#### `process_work_package()`

```
python
def process_work_package(
    api_key: str,
    folder_id: str,
    *,
    filter_start_date: Optional[date] = None,
    filter_end_date: Optional[date] = None,
    enable_action_step_control: bool = True,
    logger: Optional[Callable[[str], None]] = None
) -> List[Dict[str, Any]]:
    """
    High-level pipeline for processing work package from Drive.
    
    Steps:
    1. Authenticate to Google Drive
    2. Download all Excel files from folder
    3. Process each file with validation
    4. Return list of results
    
    Args:
        api_key: Google Drive API key
        folder_id: Google Drive folder ID
        filter_start_date: Optional start date
        filter_end_date: Optional end date
        enable_action_step_control: Whether to run ASC
        logger: Optional logging function
        
    Returns:
        List of result dicts:
        [
            {
                "source_name": "file.xlsx",
                "source_id": "1ABC...",
                "local_path": "DATA/temp_download/file.xlsx",
                "output_file": "DATA/WP_123/WP_123_10am15.xlsx"
            },
            ...
        ]
        
    Example:
        >>> results = process_work_package(
        ...     api_key="AIzaSyB...",
        ...     folder_id="1ABC...",
        ...     filter_start_date=date(2024, 1, 1)
        ... )
        >>> for r in results:
        ...     print(f"{r['source_name']}: {r['output_file']}")
    """
```

---

## Validation Module

### doc_validator.validation.engine

Core validation logic.

#### `check_ref_keywords()`

```
python
def check_ref_keywords(
    text: str,
    seq_value: Optional[str] = None,
    header_text: Optional[str] = None,
    des_text: Optional[str] = None
) -> str:
    """
    Main validation function - determines validation state.
    
    Args:
        text: wo_text_action.text content to validate
        seq_value: Optional SEQ field value
        header_text: Optional wo_text_action.header value
        des_text: Optional DES field value
        
    Returns:
        One of: "Valid", "Missing reference", "Missing revision", "N/A"
        
    Validation Logic:
    1. Check SEQ auto-valid (1.x, 2.x, 3.x, 10.x)
    2. Check header skip keywords
    3. Preserve N/A / blank
    4. Check skip phrases
    5. Auto-correct typos
    6. Check special patterns (REFERENCED, NDT, SB, etc.)
    7. Validate reference + revision
    
    Example:
        >>> check_ref_keywords("IAW AMM 52-11-01 REV 156")
        'Valid'
        
        >>> check_ref_keywords("REMOVED PANEL")
        'Missing reference'
        
        >>> check_ref_keywords("IAW AMM 52-11-01")
        'Missing revision'
        
        >>> check_ref_keywords("N/A")
        'N/A'
        
        >>> check_ref_keywords("TEXT", seq_value="1.1")
        'Valid'  # SEQ auto-valid
    """
```

### doc_validator.validation.helpers

Validation helper functions.

#### `fix_common_typos()`

```
python
def fix_common_typos(text: str) -> str:
    """
    Auto-correct common typos in maintenance documentation.
    
    Corrections:
    - REFAMM → REF AMM
    - REV156 → REV 156
    - AMM52-11-01 → AMM 52-11-01
    - REV: → REV
    - Multiple spaces → Single space
    
    Args:
        text: Input text
        
    Returns:
        Corrected text
        
    Example:
        >>> fix_common_typos("REFAMM52-11-01REV156")
        'REF AMM 52-11-01 REV 156'
    """
```

#### `has_revision()`

```
python
def has_revision(text: str) -> bool:
    """
    Check if text contains any revision indicator.
    
    Checks for:
    - REV \d+
    - ISSUE \d+
    - ISSUED SD \d+
    - TAR \d+
    - EXP date
    - DEADLINE date
    
    Args:
        text: Text to check
        
    Returns:
        True if revision found, False otherwise
        
    Example:
        >>> has_revision("AMM 52-11-01 REV 156")
        True
        
        >>> has_revision("AMM 52-11-01")
        False
    """
```

#### `has_primary_reference()`

```
python
def has_primary_reference(text: str) -> bool:
    """
    Check if text contains primary reference keyword.
    
    Keywords: AMM, SRM, CMM, EMM, MEL, NEF, SB, AD, etc.
    
    Args:
        text: Text to check
        
    Returns:
        True if reference found
        
    Example:
        >>> has_primary_reference("IAW AMM 52-11-01")
        True
        
        >>> has_primary_reference("REMOVED PANEL")
        False
    """
```

#### `is_seq_auto_valid()`

```
python
def is_seq_auto_valid(seq_value: Any) -> bool:
    """
    Check if SEQ should be automatically marked as Valid.
    
    Auto-valid patterns: 1.x, 2.x, 3.x, 10.x
    
    Args:
        seq_value: SEQ field value (string, float, or int)
        
    Returns:
        True if SEQ matches auto-valid patterns
        
    Example:
        >>> is_seq_auto_valid("1.1")
        True
        
        >>> is_seq_auto_valid("4.1")
        False
    """
```

#### `contains_header_skip_keyword()`

```
python
def contains_header_skip_keyword(header_text: str) -> bool:
    """
    Check if header contains skip keywords.
    
    Keywords: CLOSE UP, JOB SET UP, OPEN ACCESS, etc.
    
    Args:
        header_text: wo_text_action.header value
        
    Returns:
        True if skip keyword found
        
    Example:
        >>> contains_header_skip_keyword("CLOSE UP")
        True
        
        >>> contains_header_skip_keyword("TASK 1")
        False
    """
```

---

## Tools Module

### doc_validator.tools.action_step_control

Action Step Control (chronological verification).

#### `compute_action_step_control_df()`

```
python
def compute_action_step_control_df(
    df: pd.DataFrame,
    wp_col_candidates: Optional[List[str]] = None,
    wo_col_candidates: Optional[List[str]] = None,
    workstep_col_candidates: Optional[List[str]] = None,
    date_col_candidates: Optional[List[str]] = None,
    time_col_candidates: Optional[List[str]] = None,
    text_col_candidates: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, pd.DataFrame, str]:
    """
    Core logic for Action Step Control.
    
    Verifies that work steps within each Work Order are performed
    in chronological order.
    
    Args:
        df: Input DataFrame
        *_col_candidates: Lists of possible column names to search for
        
    Returns:
        Tuple of (asc_df, summary_df, wp_value):
        - asc_df: DataFrame with ActionStepOrderOK and ActionStepIssue columns
        - summary_df: Per-WO summary DataFrame
        - wp_value: Detected Work Package identifier
        
    Output Columns (asc_df):
        - All original columns
        - ActionStepOrderOK: Boolean (True/False)
        - ActionStepIssue: Description if False ("Earlier than steps X, Y")
        
    Output Columns (summary_df):
        - wo: Work Order number
        - num_worksteps: Total steps
        - status: "OK" or "VIOLATIONS"
        - num_violations: Count of timing issues
        
    Example:
        >>> asc_df, summary, wp = compute_action_step_control_df(df)
        >>> print(f"WP: {wp}")
        WP: WP_123
        >>> print(f"Violations: {summary['num_violations'].sum()}")
        Violations: 3
    """
```

### doc_validator.tools.process_local_batch

Batch processing utility.

#### `process_local_batch()`

```
python
def process_local_batch(
    folder_path: str,
    enable_action_step_control: bool = True
) -> List[Dict[str, str]]:
    """
    Process all Excel files in a local folder.
    
    Args:
        folder_path: Path to folder containing Excel files
        enable_action_step_control: Whether to run ASC
        
    Returns:
        List of result dicts:
        [
            {
                "original": "/path/to/input.xlsx",
                "output": "DATA/WP_123/WP_123_10am15.xlsx"
            },
            ...
        ]
        
    Example:
        >>> results = process_local_batch("./INPUT")
        >>> print(f"Processed {len(results)} files")
        Processed 5 files
    """
```

---

## Interface Module

### doc_validator.interface.main_window

GUI main window.

#### `MainWindow` Class

```
python
class MainWindow(QMainWindow):
    """
    Main application window for GUI.
    
    Features:
    - File selection (local/Drive)
    - Date filtering
    - Action Step Control toggle
    - Progress tracking
    - Console output
    
    Signals:
    - None (uses internal worker signals)
    
    Public Methods:
    - None (UI interactions handled internally)
    
    Example:
        >>> from doc_validator.interface.main_window import launch
        >>> launch()  # Starts GUI application
    """
```

### doc_validator.interface.panels.date_filter_panel

Date filtering UI panel.

#### `DateFilterPanel` Class

```
python
class DateFilterPanel(QGroupBox):
    """
    Reusable date filter panel.
    
    Signals:
        filter_toggled(bool): Emitted when filter enabled/disabled
        
    Public Methods:
    """
    
    def is_enabled(self) -> bool:
        """Return True if date filtering is enabled."""
        
    def get_range(self) -> Tuple[Optional[date], Optional[date]]:
        """
        Get date range from panel.
        
        Returns:
            (start_date, end_date) tuple
            Both can be None if filtering disabled
            
        Raises:
            ValueError: If date format is invalid
            
        Supported Formats:
            - Absolute: YYYY-MM-DD (e.g., "2024-01-15")
            - Relative: +/-Nd/M/Y (e.g., "-30d", "+1m")
        """
```

### doc_validator.interface.workers.processing_worker

Background processing thread.

#### `ProcessingWorker` Class

```
python
class ProcessingWorker(QThread):
    """
    Background worker for file processing.
    
    Prevents GUI freezing during long operations.
    
    Signals:
        log_message(str): Log message to display
        progress_updated(int, str): Progress (0-100, status text)
        finished_with_results(list): Processing complete with results
        
    Args:
        api_key: Google Drive API key (or None for local)
        folder_id: Google Drive folder ID (or None for local)
        selected_files: List of FileInfo objects to process
        filter_start_date: Optional start date
        filter_end_date: Optional end date
        enable_action_step_control: Whether to run ASC
        
    Example:
        >>> worker = ProcessingWorker(
        ...     api_key=None,
        ...     folder_id=None,
        ...     selected_files=[file1, file2],
        ...     enable_action_step_control=True
        ... )
        >>> worker.log_message.connect(print)
        >>> worker.start()
    """
```

---

## Configuration

### doc_validator.config

Global configuration module.

#### Constants

```
python
# Base directory (auto-detected)
BASE_DIR: Path  # Project root directory

# File paths
LINK_FILE: str  # Path to bin/link.txt (credentials)

# Output folders
DATA_FOLDER: str  # Output folder (DATA/)
INPUT_FOLDER: str  # Input folder (INPUT/)
LOG_FOLDER: str  # Log subfolder name ("log")

# Settings
INVALID_CHARACTERS: str  # Regex pattern for invalid filename chars

# Action Step Control
ACTION_STEP_CONTROL_ENABLED_DEFAULT: bool  # True
ACTION_STEP_SHEET_NAME: str  # "ActionStepControl"
ACTION_STEP_SUMMARY_ENABLED_DEFAULT: bool  # True
ACTION_STEP_SUMMARY_SHEET_NAME: str  # "ASC_Summary"
```

#### Usage

```
python
from doc_validator.config import DATA_FOLDER, INPUT_FOLDER

print(f"Output folder: {DATA_FOLDER}")
print(f"Input folder: {INPUT_FOLDER}")
```

### doc_validator.validation.constants

Validation configuration.

#### Constants

```
python
# Reference keywords (20+ types)
REF_KEYWORDS: List[str] = [
    "AMM", "SRM", "CMM", "EMM", "MEL", "NEF", "SB", "AD", ...
]

# Linking keywords
IAW_KEYWORDS: List[str] = ["IAW", "REF", "PER", "I.A.W"]

# Skip phrases
SKIP_PHRASES: List[str] = [
    "GET ACCESS", "SPARE ORDERED", ...
]

# Header skip keywords
HEADER_SKIP_KEYWORDS: List[str] = [
    "CLOSE UP", "JOB SET UP", "OPEN ACCESS", ...
]
```

---

## Type Definitions

### FileInfo

```
python
@dataclass
class FileInfo:
    """Information about an Excel file from any source."""
    name: str  # Filename
    source_type: str  # "local" or "drive"
    local_path: Optional[str] = None  # For local files
    file_id: Optional[str] = None  # For Drive files
    mime_type: Optional[str] = None  # For Drive files
```

### Logger

```
python
Logger = Callable[[str], None]  # Function that accepts log messages
```

---

## Examples

### Example 1: Process Single File

```
python
from doc_validator.core.excel_pipeline import process_excel

output = process_excel("input.xlsx")
if output:
    print(f"Success: {output}")
else:
    print("Processing failed")
```

### Example 2: Process with Date Filter

```
python
from datetime import date
from doc_validator.core.excel_pipeline import process_excel

output = process_excel(
    "input.xlsx",
    filter_start_date=date(2024, 1, 1),
    filter_end_date=date(2024, 12, 31),
    enable_action_step_control=True
)
```

### Example 3: Process from Google Drive

```
python
from doc_validator.core.pipeline import process_work_package

results = process_work_package(
    api_key="AIzaSyB...",
    folder_id="1ABC...",
    enable_action_step_control=True
)

for result in results:
    print(f"{result['source_name']}: {result['output_file']}")
```

### Example 4: Custom Logger

```
python
from doc_validator.core.pipeline import process_from_credentials_file

def my_logger(message: str):
    with open("processing.log", "a") as f:
        f.write(message + "\n")

results = process_from_credentials_file(
    "bin/link.txt",
    logger=my_logger
)
```

### Example 5: Manual Validation

```
python
from doc_validator.validation.engine import check_ref_keywords

# Test various inputs
texts = [
    "IAW AMM 52-11-01 REV 156",
    "REMOVED PANEL",
    "IAW AMM 52-11-01",
    "N/A"
]

for text in texts:
    result = check_ref_keywords(text)
    print(f"{text[:30]:<30} → {result}")
```

Output:
```
IAW AMM 52-11-01 REV 156       → Valid
REMOVED PANEL                   → Missing reference
IAW AMM 52-11-01               → Missing revision
N/A                            → N/A
```

---

## Error Handling

All functions may raise exceptions. Always use try-except:

```
python
try:
    output = process_excel("input.xlsx")
except FileNotFoundError:
    print("File not found")
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Performance Notes

- **Large files** (>50MB): May take several minutes
- **Date filtering**: Significantly reduces processing time
- **Action Step Control**: Adds ~10-20% processing time
- **Memory usage**: ~2-3x file size in RAM

---

## Version Compatibility

| Version | Python | pandas | PyQt6 |
|---------|--------|--------|-------|
| 1.25    | 3.8+   | 1.5+   | 6.0+  |
| 1.20    | 3.8+   | 1.5+   | 6.0+  |

---

## See Also

- [User Guide](USER_GUIDE.md) - End-user documentation
- [Developer Guide](DEVELOPER_GUIDE.md) - Development information
- [Validation Rules](VALIDATION_RULES.md) - Complete validation logic