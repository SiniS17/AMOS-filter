# Quick Start Guide

Get up and running with AMOS Documentation Validator in 5 minutes.

## 1. Install (2 minutes)

```bash
# Clone repository
git clone https://github.com/yourusername/amos-validator.git
cd amos-validator

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-gui.txt
```

## 2. Prepare Files (1 minute)

```bash
# Create input folder
mkdir INPUT

# Copy your Excel files to INPUT folder
cp /path/to/your/files/*.xlsx INPUT/
```

## 3. Run Validator (1 minute)

### Option A: GUI (Recommended)

```bash
python run_gui.py
```

1. Files will appear in list
2. Check files you want to process
3. Click "▶ Run Processing"
4. Click "📂 Open Output" to view results

### Option B: Command Line

```bash
python -m doc_validator.tools.process_local_batch ./INPUT
```

Results will be in `DATA/<WorkPackage>/` folders.

## 4. Review Results (1 minute)

Output files contain:
- **Sheet "REF REV"**: Main results with `Reason` column
  - ✅ `Valid` - Correct references
  - ❌ `Missing reference` - No reference found  
  - ❌ `Missing revision` - No revision number
  - ⚪ `N/A` - Blank/N/A entries

Filter by `Reason` column to find errors.

## What Next?

- **Learn more**: Read [User Guide](Docs/USER_GUIDE.md)
- **Understand validation**: See [Validation Rules](Docs/VALIDATION_RULES.md)
- **Configure**: Check [Configuration Guide](Docs/CONFIGURATION.md)
- **Get help**: Review [Troubleshooting](Docs/TROUBLESHOOTING.md)

## Common First-Time Issues

**"No files found"**
- Ensure files are in INPUT folder
- Verify files are .xlsx or .xls format

**"GUI won't start"**
- Install GUI dependencies: `pip install -r requirements-gui.txt`

**"Too many errors"**
- This is normal for first run
- Review validation rules
- Check sample errors to understand patterns

## Example Workflow

```bash
# 1. Place files in INPUT
cp WP_123.xlsx INPUT/

# 2. Run processing
python run_gui.py

# 3. Check output
ls DATA/WP_123/

# 4. Open in Excel
# File: DATA/WP_123/WP_123_10am15_21_12_24.xlsx
# Sheet: REF REV
# Filter: Reason column
```

## Next Steps

1. ✅ **Review results** - Check validation output
2. 📚 **Read documentation** - Understand validation rules
3. ⚙️ **Configure** - Customize for your needs
4. 🔄 **Integrate** - Add to your workflow

---

**Need help?** Check [Troubleshooting](Docs/TROUBLESHOOTING.md) or open an [Issue](https://github.com/yourusername/amos-validator/issues).