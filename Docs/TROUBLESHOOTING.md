# Troubleshooting Guide

Common issues and solutions for AMOS Documentation Validator.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Google Drive Issues](#google-drive-issues)
- [Processing Issues](#processing-issues)
- [Validation Issues](#validation-issues)
- [GUI Issues](#gui-issues)
- [Performance Issues](#performance-issues)
- [Data Quality Issues](#data-quality-issues)

---

## Installation Issues

### Problem: "Python is not recognized"

**Windows**:
```
'python' is not recognized as an internal or external command
```

**Solution**:
1. Add Python to PATH:
   - Search "Environment Variables" in Windows
   - Edit "Path" under System Variables
   - Add: `C:\Users\<YourName>\AppData\Local\Programs\Python\Python310\`
2. Or use full path:
   ```cmd
   C:\Users\YourName\AppData\Local\Programs\Python\Python310\python.exe run_gui.py
   ```

### Problem: "pip is not recognized"

**Solution**:
```bash
# Use python -m pip instead
python -m pip install -r requirements.txt
```

### Problem: "No module named 'pandas'"

**Symptoms**:
```
python
ImportError: No module named 'pandas'
ModuleNotFoundError: No module named 'pandas'
```

**Solution**:
```bash
# Install missing dependencies
pip install pandas openpyxl

# Or reinstall all
pip install -r requirements.txt
```

### Problem: "No module named 'PyQt6'"

**Solution**:
```bash
# Install GUI dependencies
pip install PyQt6

# Or
pip install -r requirements-gui.txt
```

### Problem: Permission denied during installation

**Linux/macOS**:
```bash
# Use --user flag
pip install --user -r requirements.txt
```

**Or use virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Problem: "Microsoft Visual C++ required" (Windows)

**Solution**:
Download and install [Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)

---

## Google Drive Issues

### Problem: "Drive credentials not configured"

**Symptoms**:
```
❌ Drive credentials not configured
No files found in the folder
```

**Solution**:
1. Create `bin` folder
2. Create `bin/link.txt`:
   ```
   GG_API_KEY=your_api_key_here
   GG_FOLDER_ID=your_folder_id_here
   ```
3. Verify API key is valid
4. Verify folder ID is correct

### Problem: "Authentication failed"

**Symptoms**:
```
❌ Error accessing Google Drive folder
Authentication error
```

**Solution**:
1. **Check API key**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - APIs & Services → Credentials
   - Verify API key exists and is not restricted incorrectly

2. **Enable Google Drive API**:
   - APIs & Services → Library
   - Search "Google Drive API"
   - Click Enable

3. **Check API key restrictions**:
   - If restricted, ensure Google Drive API is in the allowed list

### Problem: "No files found in folder"

**Symptoms**:
```
📁 Found 0 Excel file(s) in folder
```

**Solution**:
1. **Verify folder ID**:
   - Open Drive folder in browser
   - URL: `https://drive.google.com/drive/folders/1ABC...XYZ`
   - Folder ID is the part after `/folders/`

2. **Check folder permissions**:
   - Folder should be "Anyone with the link can view"
   - Or API key service account should have access

3. **Verify files are Excel**:
   - Files must be `.xlsx` or `.xls`
   - Not Google Sheets (use File → Download → Excel)

### Problem: "Failed to download file"

**Symptoms**:
```
❌ Error downloading file: <filename>
```

**Solution**:
1. Check file is not corrupted in Drive
2. Check file size (very large files may timeout)
3. Check internet connection
4. Try downloading manually to verify access

---

## Processing Issues

### Problem: Row count mismatch

**Symptoms**:
```
🔴 CRITICAL: Row count mismatch detected!
   Original rows: 450
   Output rows: 445
   LOST ROWS: 5
```

**Causes**:
1. Date filtering removed rows
2. Completely blank rows were skipped
3. Invalid date formats

**Solution**:
1. **Check DEBUG folder**:
   ```
   DATA/<WP>/DEBUG/input_original_20241221_143022.csv
   DATA/<WP>/DEBUG/output_processed_20241221_143022.csv
   ```
   Compare these files to find missing rows

2. **Review date filter settings**:
   - Check start/end dates are correct
   - Verify action_date column format is YYYY-MM-DD

3. **Check for blank rows**:
   - Excel file may have empty rows at the end
   - These are intentionally skipped

### Problem: "No data remains after date filtering"

**Symptoms**:
```
✗ No data remains after date filtering
```

**Solution**:
1. **Check date range**:
   - Verify start_date < end_date
   - Verify dates overlap with data

2. **Check action_date format**:
   - Must be YYYY-MM-DD (e.g., "2024-01-15")
   - Check for invalid dates in Excel

3. **Check file's date range**:
   - Look at start_date and end_date columns (first row)
   - These auto-filter the data

### Problem: Processing hangs or freezes

**Solution**:
1. **Check file size**:
   - Files >100MB may take >5 minutes
   - Split large files if needed

2. **Close other applications**:
   - Free up RAM

3. **Disable Action Step Control** (if enabled):
   - Reduces processing time by 10-20%
   ```bash
   python -m doc_validator.interface.cli_main --no-asc
   ```

4. **Check for infinite loops**:
   - Force quit (Ctrl+C in CLI)
   - Restart application

### Problem: "Validation error: <message>"

**Common errors**:
```
No 'wo_text_action.text' column found
DataFrame is empty
No rows to process
```

**Solution**:
1. **Check column names**:
   - Excel must have `wo_text_action.text` column
   - Column names are case-insensitive
   - Check for extra spaces in column names

2. **Check file format**:
   - Must be `.xlsx` or `.xls`
   - First row must be headers
   - Must have at least one data row

3. **Check required columns**:
   - WO
   - wo_text_action.text
   - SEQ
   - Workstep
   - action_date

---

## Validation Issues

### Problem: Too many "Missing reference" errors

**Symptoms**:
```
Error rate: 45%
Missing reference: 200+ rows
```

**Causes**:
1. Documentation quality is actually poor
2. New document types not recognized
3. DES field has references (triggering enforcement)

**Solution**:
1. **Review sample errors**:
   - Open output file
   - Filter by "Missing reference"
   - Check if they're actually missing references

2. **Add new document types** (if needed):
   - Edit `doc_validator/validation/constants.py`
   - Add to `REF_KEYWORDS` list
   - Run tests

3. **Check DES field**:
   - If DES has references, all rows need references
   - This is by design (context-aware validation)

### Problem: Valid entries marked as "Missing revision"

**Example**:
```
"IAW AMM 52-11-01 REV 156" → Missing revision
```

**Causes**:
1. Typo in revision format
2. Non-standard revision format

**Solution**:
1. **Check for typos**:
   - Extra spaces: "REV  156"
   - Missing space: "REV156" (auto-corrected)
   - Wrong separator: "REV/156"

2. **Add custom revision pattern**:
   - Edit `doc_validator/validation/patterns.py`
   - Add new pattern
   - Update `has_revision()` in `helpers.py`

### Problem: SEQ auto-valid not working

**Example**:
```
SEQ 1.1: "Setup tasks" → Missing reference
```

**Causes**:
1. SEQ format is wrong
2. Bug in validation

**Solution**:
1. **Check SEQ format**:
   - Must be exactly: "1.1", "1.2", etc.
   - Not: "1-1", "1,1", "Step 1.1"

2. **Test manually**:
   ```
python
   from doc_validator.validation.helpers import is_seq_auto_valid
   print(is_seq_auto_valid("1.1"))  # Should be True
   ```

### Problem: Header keywords not working

**Example**:
```
Header: "CLOSE UP" → Still asking for reference
```

**Causes**:
1. Header column not found
2. Header format doesn't match

**Solution**:
1. **Check column name**:
   - Must be `wo_text_action.header`
   - Case-insensitive

2. **Check header text**:
   - Must be exact: "CLOSE UP", "JOB SET UP", etc.
   - Spaces matter: "CLOSEUP" ≠ "CLOSE UP"

3. **Add custom header keyword**:
   - Edit `doc_validator/validation/constants.py`
   - Add to `HEADER_SKIP_KEYWORDS`

---

## GUI Issues

### Problem: GUI won't start

**Symptoms**:
```
ImportError: DLL load failed
Could not find Qt platform plugin
```

**Solution (Windows)**:
```bash
# Reinstall PyQt6
pip uninstall PyQt6
pip install PyQt6
```

**Solution (Linux)**:
```bash
# Install system dependencies
sudo apt install libxcb-xinerama0 libxcb-cursor0

# Reinstall PyQt6
pip install --force-reinstall PyQt6
```

**Solution (macOS)**:
```bash
# Set Qt plugin path
export QT_QPA_PLATFORM_PLUGIN_PATH=/path/to/python/site-packages/PyQt6/Qt6/plugins

# Or reinstall
pip install --force-reinstall PyQt6
```

### Problem: Files not showing in list

**Solution**:
1. **Click refresh icon** in table header
2. **Check folder path** is correct
3. **Verify files are Excel** (.xlsx or .xls)
4. **Check permissions** (can you open folder?)

### Problem: "Run Processing" button disabled

**Solution**:
1. **Select at least one file** (check boxes)
2. **Check if processing is already running**
3. **Restart application** if stuck

### Problem: Progress bar stuck at 99%

**Solution**:
- This is normal for the last file
- Wait for completion
- If truly stuck (>10 minutes), restart

### Problem: Console output not showing

**Solution**:
1. **Click "▲ Expand"** button
2. **Check if collapsed** (click toggle button)
3. **Scroll to bottom** of console

---

## Performance Issues

### Problem: Processing is very slow

**Symptoms**:
- Taking >10 minutes per file
- High CPU usage
- System unresponsive

**Solution**:
1. **Check file size**:
   - Files >50MB are slow
   - Split large files

2. **Disable Action Step Control**:
   - Saves 10-20% time
   - Uncheck "Run Action Step Control (ASC)"

3. **Use date filter**:
   - Process only necessary date range
   - Reduces rows to process

4. **Close other applications**:
   - Free up CPU and RAM

5. **Check system resources**:
   ```bash
   # Windows
   Task Manager → Performance tab
   
   # Linux
   htop
   
   # macOS
   Activity Monitor
   ```

### Problem: Out of memory error

**Symptoms**:
```
MemoryError
Python has stopped working
```

**Solution**:
1. **Close other applications**
2. **Process files one at a time**
3. **Split large Excel files**:
   - Use Excel to split into smaller files
   - Process separately

4. **Increase system RAM** (if possible)

---

## Data Quality Issues

### Problem: Invalid date format errors

**Symptoms**:
```
⚠️ Found 50 rows with invalid date format - removing them
```

**Solution**:
1. **Fix dates in Excel**:
   - Use YYYY-MM-DD format
   - Example: "2024-01-15"

2. **Check for typos**:
   - "2024-13-01" (month 13 doesn't exist)
   - "2024-01-32" (day 32 doesn't exist)
   - "01-15-2024" (wrong order)

3. **Convert dates in Excel**:
   ```excel
   =TEXT(A1,"YYYY-MM-DD")
   ```

### Problem: DES field causing false positives

**Scenario**:
```
DES: "IAW AMM 52-11-01 REV 156"
Row: "REMOVED PANEL" → Missing reference
```

**Explanation**:
This is **by design**, not a bug. When DES has a reference, all rows are expected to have references.

**Solution**:
1. **Add references to rows**:
   ```
   "REMOVED PANEL IAW REFERENCED AMM TASK"
   ```

2. **Or remove reference from DES** if it applies to all rows

3. **Or use cross-references**:
   ```
   "REMOVED PANEL - REFER RESULT WT 8"
   ```

### Problem: Missing columns error

**Symptoms**:
```
Required column(s) not found
'action_date' column not found
```

**Solution**:
1. **Add missing columns** to Excel file
2. **Check column name spelling**:
   - Case doesn't matter: "ACTION_DATE" = "action_date"
   - Underscores matter: "actiondate" ≠ "action_date"

3. **Check for hidden columns** in Excel

4. **Required columns**:
   - WO
   - wo_text_action.text
   - SEQ
   - Workstep
   - action_date
   - action_time (for ASC)

---

## Common Error Messages

### "FileNotFoundError: [Errno 2] No such file or directory"

**Cause**: Input file doesn't exist

**Solution**:
- Check file path is correct
- Use absolute path if relative path fails
- Verify file extension (.xlsx or .xls)

### "PermissionError: [Errno 13] Permission denied"

**Cause**: File is open in Excel or no write permission

**Solution**:
- Close Excel file
- Check folder permissions
- Run as administrator (Windows)

### "BadZipFile: File is not a zip file"

**Cause**: File is corrupted or not actually an Excel file

**Solution**:
- Re-download file
- Save as .xlsx from Excel
- Try different Excel file

### "KeyError: 'wo_text_action.text'"

**Cause**: Required column missing

**Solution**:
- Add `wo_text_action.text` column
- Check spelling and spacing
- Rename column if needed

---

## Getting More Help

### Check Logs

**Logbook location**:
```
DATA/log/logbook_YYYY_MM.xlsx
```

Review:
- Error rates
- Processing times
- Row mismatches

### Debug Mode

Enable detailed logging:

```
python
# In your script
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Report a Bug

When reporting issues, include:

1. **Version**: Check `version_label` in GUI or run:
   ```bash
   python -c "import doc_validator; print(doc_validator.__version__)"
   ```

2. **Error message**: Full text from console

3. **Steps to reproduce**:
   - What you did
   - What happened
   - What you expected

4. **System info**:
   - OS and version
   - Python version: `python --version`
   - Installed packages: `pip list`

5. **Sample data** (if possible):
   - Small Excel file that reproduces issue
   - Remove sensitive data

### Community Support

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and help
- **Documentation**: Check all docs in `docs/` folder

---

## Prevention Tips

### Best Practices

1. **Regular backups**:
   - Backup input files
   - Save logbooks monthly

2. **Test with small samples**:
   - Process 1-2 files first
   - Verify results before batch processing

3. **Keep software updated**:
   - Update Python packages regularly
   - Check for validator updates

4. **Clean your data**:
   - Fix dates before processing
   - Remove blank rows
   - Ensure column names are correct

5. **Monitor logbook**:
   - Review error rates monthly
   - Identify patterns
   - Address recurring issues

### Data Quality Checklist

Before processing:
- [ ] Files are .xlsx or .xls format
- [ ] All required columns present
- [ ] Dates in YYYY-MM-DD format
- [ ] No completely blank rows
- [ ] Column names have no typos
- [ ] Test with one file first

---

**Still having issues?** Open a [GitHub Issue](https://github.com/yourusername/amos-validator/issues) with details.