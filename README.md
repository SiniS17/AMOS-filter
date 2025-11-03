# Documentation Validator

A Python tool that validates aviation maintenance documentation by checking for proper references (AMM, SRM, etc.) and revision dates.

## Features

- ✅ Downloads Excel files from Google Drive
- ✅ Validates documentation references (AMM, SRM, CMM, etc.)
- ✅ Checks for revision dates and formats
- ✅ Detects suspicious formatting patterns
- ✅ Generates detailed validation reports
- ✅ Creates log files with error statistics

## Project Structure

```
Static filter/
├── main.py                # Main script
├── config.py              # Configuration and constants
├── validators.py          # All validation functions
├── drive_utils.py         # Google Drive functions
├── excel_utils.py         # Excel processing functions
├── link.txt               # Your API keys (not in repo)
├── requirements.txt       # Python dependencies
├── tests/                 # Testing folder
│   └── test_validators.py
├── DATA/                  # Output folder (created automatically)
└── README.md             # This file
```

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `link.txt` file in the root directory with your credentials:
```
GG_API_KEY=your_google_drive_api_key_here
GG_FOLDER_ID=your_folder_id_here
```

## Usage

### Running the Main Script

```bash
python main.py
```

This will:
1. Download the Excel file from Google Drive
2. Validate all documentation entries
3. Generate a processed file with validation results
4. Create a log file with error statistics

### Running Tests

```bash
# Using pytest
python -m pytest tests/test_validators.py

# Or directly
python tests/test_validators.py
```

## Validation Rules

### Reference Documentation
- **Valid**: Contains reference keywords (AMM, SRM, CMM, etc.)
- **Missing reference documentation**: No reference keywords AND no linking words (IAW, REF, PER)
- **Missing reference type**: Has linking words but no specific reference type

### Revision Date
- **Valid formats**: `REV 158`, `REV158`, `REV:158`, `REV.158`, `REV: 158`
- **Suspicious**: Multiple spaces between REV and number (e.g., `REV  158`)
- **Missing**: No revision information found

### Skip Phrases
These phrases automatically pass validation:
- GET ACCESS / GAIN ACCESS / GAINED ACCESS
- SPARE ORDERED / ORDERED SPARE

## Output

### Processed Excel File
Located in `DATA/{wp_value}/WP_{wp_value}_{timestamp}.xlsx`

Contains original data plus a "Reason" column with validation results:
- "Valid documentation"
- "Missing reference documentation"
- "Missing reference type"
- "Missing revision date"
- "Suspicious revision format"

### Log File
Located in `DATA/{wp_value}/log/WP_{wp_value}_{timestamp}.txt`

Contains statistics:
- Total rows with missing revision date
- Total rows with missing reference documentation
- Total rows with missing reference type
- Total rows with suspicious revision format
- Total rows with errors

## Configuration

Edit `config.py` to modify:
- Reference keywords (AMM, SRM, etc.)
- Linking keywords (IAW, REF, PER)
- Skip phrases
- Folder paths

## Example

Input text:
```
REMOVE AND KEEP FLOOR PANELS. REFER TO 787 AMM DMCB787-A-53-01-01-00B-520A-A REV 158
```

Output:
```
Reason: Valid documentation
```

Input text:
```
DO INSPECTION TASK WITHOUT REFERENCE
```

Output:
```
Reason: Missing reference documentation, Missing revision date
```

## Development

### Adding New Validation Rules

1. Add the rule to `validators.py`
2. Update the reason dictionary in `config.py`
3. Add tests to `tests/test_validators.py`
4. Run tests to verify

### Module Organization

- **config.py**: All constants and configuration
- **validators.py**: Validation logic (no I/O)
- **drive_utils.py**: Google Drive operations
- **excel_utils.py**: Excel file processing
- **main.py**: Orchestrates the workflow

## Troubleshooting

### "No files found in the folder"
- Check your `GG_FOLDER_ID` in `link.txt`
- Ensure the folder has at least one file
- Verify API key has access to the folder

### "API Key or Folder ID not found"
- Ensure `link.txt` exists in the root directory
- Check the format: `GG_API_KEY=...` and `GG_FOLDER_ID=...`

### Import errors when running tests
- Make sure you're running from the project root
- The test file adds the parent directory to the path automatically

## License

MIT License - feel free to use and modify as needed.