# Developer Guide

Complete guide for developers contributing to AMOS Documentation Validator.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Architecture](#project-architecture)
- [Code Structure](#code-structure)
- [Adding Features](#adding-features)
- [Testing](#testing)
- [Code Style](#code-style)
- [Building & Deployment](#building--deployment)
- [Contributing](#contributing)

---

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- Code editor (VS Code, PyCharm, etc.)
- Basic knowledge of pandas, PyQt6

### Setting Up Dev Environment

```bash
# Clone repository
git clone https://github.com/yourusername/amos-validator.git
cd amos-validator

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-gui.txt
pip install -r requirements-dev.txt  # Development tools
```

### Development Dependencies

Create `requirements-dev.txt`:
```
pytest>=7.0.0
pytest-cov>=3.0.0
black>=22.0.0
flake8>=4.0.0
mypy>=0.950
pylint>=2.13.0
```

### IDE Setup

#### VS Code

Create `.vscode/settings.json`:
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "editor.formatOnSave": true
}
```

#### PyCharm

1. File → Settings → Project → Python Interpreter
2. Select the virtual environment
3. Enable "Format code on save"
4. Set line length to 88 (Black standard)

---

## Project Architecture

### Module Overview

```
doc_validator/
├── config.py                   # Global configuration
├── core/                       # Core business logic
│   ├── drive_io.py            # Google Drive I/O
│   ├── excel_io.py            # Excel file operations
│   ├── excel_pipeline.py      # Main processing pipeline
│   ├── input_source_manager.py # File source management
│   └── pipeline.py            # High-level orchestration
├── interface/                  # User interfaces
│   ├── cli_main.py            # CLI entry point
│   ├── main_window.py         # GUI main window
│   ├── panels/                # UI panels
│   ├── styles/                # Theming
│   ├── widgets/               # Custom widgets
│   └── workers/               # Background threads
├── validation/                 # Validation engine
│   ├── constants.py           # Configuration
│   ├── engine.py              # Main validation logic
│   ├── helpers.py             # Helper functions
│   └── patterns.py            # Regex patterns
├── tools/                      # Utility scripts
│   ├── action_step_control.py
│   ├── diagnose_row_loss.py
│   └── process_local_batch.py
└── tests/                      # Test suites
    ├── test_validators.py
    └── test_real_world_data.py
```

### Data Flow

```
┌──────────────┐
│ Input Source │ (Local/Drive)
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ File Manager │ (input_source_manager.py)
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ Excel Reader │ (excel_io.py)
└──────┬───────┘
       │
       ↓
┌──────────────┐
│   Pipeline   │ (excel_pipeline.py)
└──────┬───────┘
       │
       ├─→ Date Filter
       ├─→ Column Prep
       ├─→ Validation Engine
       │   └─→ (validation/engine.py)
       └─→ Action Step Control
           └─→ (tools/action_step_control.py)
       │
       ↓
┌──────────────┐
│ Excel Writer │ (excel_io.py)
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ Output Files │ (DATA folder)
└──────────────┘
```

### Key Design Patterns

#### 1. Pipeline Pattern

```
python
# excel_pipeline.py
def process_excel(file_path, filter_start_date=None, ...):
    # Step 1: Read
    df = read_input_excel(file_path)
    
    # Step 2: Filter
    df = apply_date_filter(df, filter_start_date, ...)
    
    # Step 3: Validate
    df["Reason"] = df.apply(lambda row: check_ref_keywords(...), axis=1)
    
    # Step 4: Write
    write_output_excel(df, output_file)
```

#### 2. Strategy Pattern

```
python
# validation/engine.py
def check_ref_keywords(text, seq_value=None, ...):
    # Different validation strategies based on input
    if is_seq_auto_valid(seq_value):
        return "Valid"
    if contains_header_skip_keyword(header_text):
        return "Valid"
    # ... more strategies
```

#### 3. Worker Thread Pattern

```
python
# interface/workers/processing_worker.py
class ProcessingWorker(QThread):
    def run(self):
        # Long-running task in background
        results = process_files(...)
        self.finished_with_results.emit(results)
```

---

## Code Structure

### Core Modules

#### config.py

Global configuration constants:

```
python
# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_FOLDER = str(BASE_DIR / "DATA")
INPUT_FOLDER = str(BASE_DIR / "INPUT")

# Settings
ACTION_STEP_CONTROL_ENABLED_DEFAULT = True
```

#### excel_pipeline.py

Main processing logic:

```
python
def process_excel(file_path, filter_start_date=None, ...):
    """
    Process Excel file with validation.
    
    Args:
        file_path: Path to input file
        filter_start_date: Optional start date
        filter_end_date: Optional end date
        enable_action_step_control: Whether to run ASC
        
    Returns:
        Output file path or None on error
    """
```

#### validation/engine.py

Core validation logic:

```
python
def check_ref_keywords(text, seq_value=None, header_text=None, des_text=None):
    """
    Main validation function.
    
    Returns one of: "Valid", "Missing reference", "Missing revision", "N/A"
    
    Logic:
    1. Check SEQ auto-valid
    2. Check header keywords
    3. Preserve N/A
    4. Check skip phrases
    5. Auto-correct typos
    6. Check special patterns
    7. Validate reference + revision
    """
```

### Validation Modules

#### constants.py

Configuration for validation:

```
python
REF_KEYWORDS = ["AMM", "SRM", "CMM", ...]
IAW_KEYWORDS = ["IAW", "REF", "PER", ...]
SKIP_PHRASES = ["GET ACCESS", "SPARE ORDERED", ...]
HEADER_SKIP_KEYWORDS = ["CLOSE UP", "JOB SET UP", ...]
```

#### patterns.py

Regex patterns:

```
python
DMC_PATTERN = re.compile(r'\bDMC-?[A-Z0-9\-]+\b', re.IGNORECASE)
REV_PATTERN = re.compile(r'\bREV\s*[:\.]?\s*\d+\b', re.IGNORECASE)
```

#### helpers.py

Helper functions:

```
python
def fix_common_typos(text: str) -> str:
    """Normalize common typos."""
    
def has_revision(text: str) -> bool:
    """Check if text contains revision indicator."""
    
def has_primary_reference(text: str) -> bool:
    """Check if text contains reference keyword."""
```

### GUI Modules

#### main_window.py

Main application window:

```
python
class MainWindow(QMainWindow):
    def __init__(self):
        # Setup UI
        self._setup_ui()
        # Load credentials
        self._load_credentials()
        # Load files
        self._load_files_from_current_source()
```

#### panels/

Reusable UI components:

```
python
# date_filter_panel.py
class DateFilterPanel(QGroupBox):
    def is_enabled(self) -> bool:
        """Return True if filtering enabled."""
        
    def get_range(self) -> Tuple[Optional[date], Optional[date]]:
        """Return (start, end) date range."""
```

#### workers/processing_worker.py

Background processing:

```
python
class ProcessingWorker(QThread):
    log_message = pyqtSignal(str)
    progress_updated = pyqtSignal(int, str)
    finished_with_results = pyqtSignal(list)
    
    def run(self):
        # Process files in background
```

---

## Adding Features

### Adding a New Reference Type

1. **Update constants.py**:
```
python
REF_KEYWORDS = [
    "AMM", "SRM", "CMM",
    "MY_NEW_TYPE",  # Add here
]
```

2. **Add test cases**:
```
python
# tests/test_validators.py
def test_my_new_type():
    results.assert_equal(
        check_ref_keywords("IAW MY_NEW_TYPE 123 REV 45"),
        "Valid",
        "My new type with revision"
    )
```

3. **Run tests**:
```bash
python -m doc_validator.tests.test_validators
```

4. **Update documentation**:
- Update `VALIDATION_RULES.md`
- Add examples

### Adding a New Revision Pattern

1. **Define pattern in patterns.py**:
```
python
MY_REV_PATTERN = re.compile(r'\bMYREV\s*\d+\b', re.IGNORECASE)
```

2. **Update has_revision() in helpers.py**:
```
python
def has_revision(text: str) -> bool:
    # ... existing checks ...
    if MY_REV_PATTERN.search(text):
        return True
    return False
```

3. **Add tests and docs**

### Adding a New Special Pattern

1. **Define pattern in patterns.py**:
```
python
MY_SPECIAL_PATTERN = re.compile(r'\bMY\s+PATTERN\b', re.IGNORECASE)
```

2. **Create helper in helpers.py**:
```
python
def has_my_special_pattern(text: str) -> bool:
    if not isinstance(text, str):
        return False
    return bool(MY_SPECIAL_PATTERN.search(text))
```

3. **Update engine.py**:
```
python
def check_ref_keywords(text, ...):
    # ... existing logic ...
    
    # Add special pattern check
    if has_my_special_pattern(cleaned):
        return "Valid"
    
    # ... rest of logic ...
```

4. **Add tests**

### Adding a New GUI Panel

1. **Create panel file**:
```
python
# interface/panels/my_panel.py
from PyQt6.QtWidgets import QGroupBox

class MyPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("My Panel Title", parent)
        self._setup_ui()
        
    def _setup_ui(self):
        # Build UI components
        pass
```

2. **Integrate into main_window.py**:
```
python
from doc_validator.interface.panels.my_panel import MyPanel

class MainWindow(QMainWindow):
    def _setup_ui(self):
        # ... existing code ...
        
        self.my_panel = MyPanel(self)
        left_layout.addWidget(self.my_panel)
```

---

## Testing

### Running Tests

```bash
# Run all tests
python -m doc_validator.tests.test_validators
python -m doc_validator.tests.test_real_world_data

# Run with pytest (if installed)
pytest doc_validator/tests/

# Run with coverage
pytest --cov=doc_validator doc_validator/tests/
```

### Writing Tests

#### Unit Test Example

```
python
# tests/test_validators.py
def test_my_feature():
    """Test my new feature."""
    print("\n=== Testing My Feature ===")
    
    results.assert_equal(
        check_ref_keywords("TEST INPUT"),
        "Expected Result",
        "Test description"
    )
```

#### Integration Test Example

```
python
# tests/test_integration.py
def test_full_pipeline():
    """Test complete processing pipeline."""
    # Create test file
    test_file = "test_data.xlsx"
    
    # Process
    output = process_excel(test_file)
    
    # Verify
    assert output is not None
    assert os.path.exists(output)
```

### Test Data

Create test Excel files in `tests/data/`:

```
tests/
├── data/
│   ├── sample_valid.xlsx
│   ├── sample_errors.xlsx
│   └── sample_mixed.xlsx
└── test_validators.py
```

---

## Code Style

### Python Style Guide

Follow PEP 8 with these specifics:

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Imports**: Group by stdlib, third-party, local

### Formatting with Black

```bash
# Format all Python files
black doc_validator/

# Check without modifying
black --check doc_validator/
```

### Linting with Flake8

```bash
# Run linter
flake8 doc_validator/

# With specific rules
flake8 --max-line-length=88 --extend-ignore=E203 doc_validator/
```

### Type Hints

Use type hints where beneficial:

```
python
from typing import Optional, List, Dict, Tuple
from datetime import date

def process_excel(
    file_path: str,
    filter_start_date: Optional[date] = None,
    filter_end_date: Optional[date] = None,
    enable_action_step_control: bool = True
) -> Optional[str]:
    """Process Excel file."""
    pass
```

### Docstrings

Use Google-style docstrings:

```
python
def my_function(arg1: str, arg2: int) -> bool:
    """
    One-line summary.
    
    Detailed description of what the function does,
    including any important notes or caveats.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When input is invalid
        
    Example:
        >>> my_function("test", 42)
        True
    """
    pass
```

### Code Organization

```
python
# 1. Imports (grouped)
import os
from pathlib import Path

import pandas as pd
from PyQt6.QtWidgets import QWidget

from doc_validator.config import DATA_FOLDER

# 2. Constants
DEFAULT_VALUE = 10

# 3. Classes
class MyClass:
    pass

# 4. Functions
def my_function():
    pass

# 5. Main execution
if __name__ == "__main__":
    main()
```

---

## Building & Deployment

### Building Standalone Executable

Using PyInstaller:

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller AMOSFilter.spec

# Output location
# Windows: EXE/AMOS Validation/AMOS Validation.exe
# macOS: dist/AMOS Validation.app
# Linux: dist/AMOS Validation
```

### spec File Configuration

`AMOSFilter.spec`:
```
python
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['run_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('bin', 'bin'),
        ('doc_validator/resources', 'doc_validator/resources'),
    ],
    hiddenimports=[
        'googleapiclient.discovery',
        'pandas',
        'openpyxl',
        'PyQt6.QtCore',
    ],
    # ...
)

exe = EXE(
    # ...
    name='AMOS Validation',
    icon='doc_validator/resources/icons/app_logo.ico',
)
```

### Distribution

1. **Package structure**:
```
AMOS-Validator-v1.25/
├── AMOS Validation.exe (or app/binary)
├── bin/
│   └── link.txt.template
├── INPUT/
├── README.txt
└── docs/
    └── USER_GUIDE.pdf
```

2. **Create installer** (optional):
   - Windows: Use Inno Setup
   - macOS: Use create-dmg
   - Linux: Create .deb or .rpm

### Version Management

Update version in:
1. `doc_validator/__init__.py`:
   ```
python
   __version__ = "1.25.0"
   ```

2. `interface/main_window.py`:
   ```
python
   version_label = QLabel("BETA v1.25")
   ```

3. `CHANGELOG.md`

---

## Contributing

### Contribution Workflow

1. **Fork the repository**
2. **Create feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make changes**:
   - Write code
   - Add tests
   - Update docs

4. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

5. **Push to fork**:
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Create Pull Request**

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

**Examples**:
```
feat(validation): add support for DDG references

Add DDG (Dispatch Deviation Guide) to list of valid
reference keywords and update tests.

Closes #123

---

fix(gui): resolve file selection bug

Fixed issue where deselect all was not working properly
when search filter was active.

Fixes #456
```

### Code Review Checklist

Before submitting PR:

- [ ] Code follows style guide
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
- [ ] Commit messages are clear
- [ ] PR description explains changes

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation

## Testing
How has this been tested?

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code follows style guide
```

---

## Debugging

### Common Development Issues

**Issue: Import errors**
```bash
# Solution: Install in development mode
pip install -e .
```

**Issue: GUI not updating**
```
python
# Solution: Force repaint
self.widget.update()
self.widget.repaint()
QApplication.processEvents()
```

**Issue: Tests failing**
```bash
# Solution: Check test data
ls -la tests/data/

# Regenerate test data if needed
python generate_test_data.py
```

### Debugging Tools

**Print debugging**:
```
python
print(f"DEBUG: {variable}")
import traceback; traceback.print_exc()
```

**Using debugger**:
```
python
import pdb; pdb.set_trace()
```

**Logging**:
```
python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

---

## Resources

### Documentation

- [pandas docs](https://pandas.pydata.org/docs/)
- [PyQt6 docs](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Python docs](https://docs.python.org/3/)

### Tools

- [Black formatter](https://black.readthedocs.io/)
- [Flake8 linter](https://flake8.pycqa.org/)
- [pytest](https://docs.pytest.org/)
- [PyInstaller](https://pyinstaller.org/)

### Community

- GitHub Issues
- GitHub Discussions
- Stack Overflow (tag: `amos-validator`)

---

## FAQ for Developers

**Q: How do I add a new column to the output?**

A: Update `output_columns` list in `excel_io.py`:
```
python
output_columns = [
    "WO", "SEQ", "Workstep", ...,
    "MyNewColumn",  # Add here
]
```

**Q: How do I modify the validation logic?**

A: Edit `validation/engine.py` `check_ref_keywords()` function. Add tests.

**Q: How do I add a new input source (e.g., SharePoint)?**

A: 
1. Create `SharePointManager` in `core/`
2. Update `InputSourcePanel` to include new option
3. Update `ProcessingWorker` to handle new source

**Q: Where are cached/temp files stored?**

A: 
- Downloaded Drive files: `DATA/temp_download/`
- Debug files: `DATA/<WP>/DEBUG/`
- Logs: `DATA/log/`

---

**Next Steps**:
- Review [API Reference](API_REFERENCE.md) for detailed function docs
- Check [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines
- Join GitHub Discussions for questions