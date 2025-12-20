# AMOS Documentation Validator

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-beta-yellow.svg)]()

> Professional aircraft maintenance documentation validator for AMOS work orders

![AMOS Validator Screenshot](docs/images/screenshot.png)

## 🚀 Overview

AMOS Documentation Validator is a Python application designed to validate aircraft maintenance documentation for compliance with industry standards. It processes Excel files containing work orders and verifies that documentation references (AMM, SRM, CMM, etc.) are properly cited with revision numbers.

### Key Features

- ✅ **Multi-source Input** - Process files from local folders or Google Drive
- 📦 **Batch Processing** - Handle multiple Excel files simultaneously
- 🔍 **Smart Validation** - 4-state validation system with auto-correction
- ⏱️ **Action Step Control** - Verify chronological order of maintenance steps
- 📅 **Date Filtering** - Filter work orders by date range
- 🖥️ **Dual Interface** - Both GUI and CLI available
- 📊 **Detailed Logging** - Monthly logbook with processing statistics
- 🎯 **High Accuracy** - Handles 20+ document types with 95%+ accuracy

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## 🔧 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- 4GB RAM minimum

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/amos-validator.git
cd amos-validator

# Install dependencies
pip install -r requirements.txt
```

### GUI Installation (with PyQt6)

```bash
# Install GUI dependencies
pip install -r requirements-gui.txt
```

### Google Drive Integration (Optional)

To enable Google Drive file access:

1. Create a Google Cloud Project
2. Enable Google Drive API
3. Generate an API Key
4. Create `bin/link.txt` with:
   ```
   GG_API_KEY=your_api_key_here
   GG_FOLDER_ID=your_folder_id_here
   ```

See [Google Drive Setup Guide](docs/GOOGLE_DRIVE_SETUP.md) for detailed instructions.

## 🚀 Quick Start

### Using the GUI

```bash
python run_gui.py
```

1. Select input source (Local folder or Google Drive)
2. Choose files to process
3. Optionally set date filter
4. Click "Run Processing"

### Using the CLI

```bash
# Process from Google Drive (using bin/link.txt)
python -m doc_validator.interface.cli_main

# Process from custom credentials file
python -m doc_validator.interface.cli_main path/to/credentials.txt

# Disable Action Step Control
python -m doc_validator.interface.cli_main --no-asc
```

### Batch Processing Local Files

```bash
python -m doc_validator.tools.process_local_batch ./INPUT
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[User Guide](docs/USER_GUIDE.md)** - Complete guide for end users
- **[Installation Guide](docs/INSTALLATION.md)** - Detailed installation instructions
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - For contributors and developers
- **[Validation Rules](docs/VALIDATION_RULES.md)** - Complete validation logic documentation
- **[API Reference](docs/API_REFERENCE.md)** - Module and function documentation
- **[Configuration Guide](docs/CONFIGURATION.md)** - Configuration options
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Changelog](CHANGELOG.md)** - Version history

## 💡 Usage Examples

### Example 1: Basic Validation

```python
from doc_validator.core.excel_pipeline import process_excel

# Process a single file
output_file = process_excel("input.xlsx")
print(f"Processed file saved to: {output_file}")
```

### Example 2: With Date Filtering

```python
from datetime import date
from doc_validator.core.excel_pipeline import process_excel

# Process with date filter
output_file = process_excel(
    "input.xlsx",
    filter_start_date=date(2024, 1, 1),
    filter_end_date=date(2024, 12, 31)
)
```

### Example 3: Batch Processing

```python
from doc_validator.core.pipeline import process_from_credentials_file

# Process all files from Google Drive
results = process_from_credentials_file(
    credentials_path="bin/link.txt",
    enable_action_step_control=True
)

for result in results:
    print(f"{result['source_name']}: {result['output_file']}")
```

## ⚙️ Configuration

Key configuration files:

- `doc_validator/config.py` - Main configuration
- `bin/link.txt` - Google Drive credentials (create from template)
- `doc_validator/validation/constants.py` - Validation rules

### Key Settings

```python
# Action Step Control
ACTION_STEP_CONTROL_ENABLED_DEFAULT = True

# Date filtering
# Supports YYYY-MM-DD or relative formats (+/-Nd/M/Y)

# Output folders
DATA_FOLDER = "./DATA"  # Processed files
INPUT_FOLDER = "./INPUT"  # Local input files
```

## 🧪 Running Tests

```bash
# Run all tests
python -m doc_validator.tests.test_validators
python -m doc_validator.tests.test_real_world_data

# Run specific test
python -m unittest doc_validator.tests.test_validators.TestValidators
```

## 🛠️ Development

### Setting Up Development Environment

```bash
# Clone and install in development mode
git clone https://github.com/yourusername/amos-validator.git
cd amos-validator
pip install -e .
pip install -r requirements-dev.txt
```

### Code Style

This project follows:
- PEP 8 style guide
- Type hints where applicable
- Docstring conventions (Google style)

### Building Executable

```bash
# Build standalone executable
pyinstaller AMOSFilter.spec
```

The executable will be created in `EXE/AMOS Validation/`

## 📊 Validation States

The validator uses a 4-state system:

1. **Valid** ✅ - Has proper reference and revision
2. **Missing reference** ❌ - No reference documentation found
3. **Missing revision** ❌ - Has reference but no revision number
4. **N/A** ⚪ - Blank or N/A entries (preserved as-is)

See [Validation Rules](docs/VALIDATION_RULES.md) for complete logic.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for aircraft maintenance professionals
- Supports Boeing 787 documentation standards
- Compatible with AMOS maintenance system

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/amos-validator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/amos-validator/discussions)

## 🗺️ Roadmap

- [ ] Web-based interface
- [ ] Support for additional aircraft types
- [ ] Integration with more maintenance systems
- [ ] Real-time validation API
- [ ] Machine learning for reference detection

---

**Made with ❤️ for aviation maintenance professionals**