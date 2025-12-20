# Installation Guide

Complete installation instructions for AMOS Documentation Validator on Windows, macOS, and Linux.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Windows Installation](#windows-installation)
- [macOS Installation](#macos-installation)
- [Linux Installation](#linux-installation)
- [Google Drive Setup](#google-drive-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements

- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.8 or higher
- **RAM**: 4GB minimum
- **Storage**: 500MB for application + space for data files
- **Display**: 1280x720 minimum resolution (for GUI)

### Recommended Requirements

- **Python**: 3.10 or higher
- **RAM**: 8GB or more
- **Storage**: 2GB+ available space
- **Display**: 1920x1080 or higher

### Software Dependencies

All dependencies are listed in `requirements.txt` and will be installed automatically.

---

## Installation Methods

Choose one of the following installation methods:

1. **Standard Installation** - Full Python environment with GUI
2. **CLI-Only Installation** - Command-line interface only (lighter)
3. **Standalone Executable** - No Python required (Windows only)
4. **Development Installation** - For contributors

---

## Windows Installation

### Method 1: Standard Installation (Recommended)

#### Step 1: Install Python

1. Download Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. ✅ **IMPORTANT**: Check "Add Python to PATH"
4. Click "Install Now"
5. Verify installation:
   ```cmd
   python --version
   ```
   Should show: `Python 3.10.x` or higher

#### Step 2: Download AMOS Validator

**Option A: Using Git**
```cmd
git clone https://github.com/yourusername/amos-validator.git
cd amos-validator
```

**Option B: Manual Download**
1. Go to GitHub repository
2. Click "Code" → "Download ZIP"
3. Extract to `C:\amos-validator\`
4. Open Command Prompt in that folder

#### Step 3: Install Dependencies

```cmd
# Install core dependencies
pip install -r requirements.txt

# Install GUI dependencies
pip install -r requirements-gui.txt
```

If you encounter permission errors:
```cmd
pip install --user -r requirements.txt
pip install --user -r requirements-gui.txt
```

#### Step 4: Verify Installation

```cmd
# Test CLI
python -m doc_validator.interface.cli_main --help

# Test GUI
python run_gui.py
```

### Method 2: Standalone Executable (No Python Required)

#### Download Pre-Built Executable

1. Go to [Releases](https://github.com/yourusername/amos-validator/releases)
2. Download `AMOS-Validator-Windows.zip`
3. Extract to a folder (e.g., `C:\AMOS-Validator\`)
4. Run `AMOS Validation.exe`

#### Build Your Own Executable

If you have Python installed:

```cmd
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller AMOSFilter.spec

# Executable will be in: EXE\AMOS Validation\
```

### Common Windows Issues

**Issue: "Python is not recognized"**
- Solution: Add Python to PATH manually:
  1. Search for "Environment Variables" in Windows
  2. Edit "Path" under System Variables
  3. Add: `C:\Users\<YourName>\AppData\Local\Programs\Python\Python310\`

**Issue: "pip is not recognized"**
```cmd
python -m pip install -r requirements.txt
```

**Issue: "Microsoft Visual C++ required"**
- Download and install [Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)

---

## macOS Installation

### Step 1: Install Python

**Option A: Using Homebrew (Recommended)**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.10
```

**Option B: Download from Python.org**
1. Download Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. Run the `.pkg` installer
3. Follow installation prompts

Verify:
```bash
python3 --version
```

### Step 2: Download AMOS Validator

```bash
# Clone repository
git clone https://github.com/yourusername/amos-validator.git
cd amos-validator
```

### Step 3: Install Dependencies

```bash
# Install core dependencies
pip3 install -r requirements.txt

# Install GUI dependencies
pip3 install -r requirements-gui.txt
```

### Step 4: Verify Installation

```bash
# Test CLI
python3 -m doc_validator.interface.cli_main

# Test GUI
python3 run_gui.py
```

### macOS-Specific Notes

**Qt Platform Plugin Issue**
If you see "Could not find the Qt platform plugin":
```bash
export QT_QPA_PLATFORM_PLUGIN_PATH=/path/to/python/site-packages/PyQt6/Qt6/plugins
```

**Permission Issues**
```bash
# Use --user flag
pip3 install --user -r requirements.txt
```

**Create Application Alias**
```bash
# Add to ~/.zshrc or ~/.bash_profile
alias amos-validator="python3 /path/to/amos-validator/run_gui.py"
```

---

## Linux Installation

### Ubuntu/Debian

#### Step 1: Install Python and Dependencies

```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3.10 python3-pip python3-venv

# Install system dependencies for PyQt6
sudo apt install libxcb-xinerama0 libxcb-cursor0
```

#### Step 2: Download AMOS Validator

```bash
# Clone repository
git clone https://github.com/yourusername/amos-validator.git
cd amos-validator
```

#### Step 3: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

#### Step 4: Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install GUI dependencies
pip install -r requirements-gui.txt
```

#### Step 5: Verify Installation

```bash
# Test CLI
python -m doc_validator.interface.cli_main

# Test GUI
python run_gui.py
```

### Red Hat/CentOS/Fedora

```bash
# Install Python
sudo dnf install python3.10 python3-pip

# Clone and install (same as Ubuntu)
git clone https://github.com/yourusername/amos-validator.git
cd amos-validator
pip install -r requirements.txt
pip install -r requirements-gui.txt
```

### Arch Linux

```bash
# Install Python
sudo pacman -S python python-pip

# Clone and install (same as above)
```

### Create Desktop Entry (Optional)

```bash
# Create desktop file
cat > ~/.local/share/applications/amos-validator.desktop << EOF
[Desktop Entry]
Type=Application
Name=AMOS Validator
Comment=Aircraft Maintenance Documentation Validator
Exec=/path/to/venv/bin/python /path/to/amos-validator/run_gui.py
Icon=/path/to/amos-validator/doc_validator/resources/icons/app_logo.png
Terminal=false
Categories=Office;
EOF
```

---

## Google Drive Setup

To enable Google Drive file processing:

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (e.g., "AMOS Validator")
3. Enable **Google Drive API**:
   - Go to "APIs & Services" → "Library"
   - Search for "Google Drive API"
   - Click "Enable"

### Step 2: Create API Key

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "API Key"
3. Copy the API key (it will look like: `AIzaSyB...`)
4. (Recommended) Click "Restrict Key":
   - Under "API restrictions", select "Restrict key"
   - Choose "Google Drive API"
   - Save

### Step 3: Get Folder ID

1. Open Google Drive in your browser
2. Navigate to the folder containing your Excel files
3. Look at the URL: `https://drive.google.com/drive/folders/1ABC...XYZ`
4. The Folder ID is the part after `/folders/`: `1ABC...XYZ`

### Step 4: Configure AMOS Validator

1. Create `bin` folder in the application directory:
   ```bash
   mkdir bin
   ```

2. Create `bin/link.txt` with this content:
   ```
   GG_API_KEY=your_api_key_here
   GG_FOLDER_ID=your_folder_id_here
   ```

3. Example:
   ```
   GG_API_KEY=AIzaSyB1234567890abcdefGHIJKLMNOP
   GG_FOLDER_ID=1ABCdefGHIjklMNOpqrSTUvwxYZ
   ```

### Step 5: Test Connection

```bash
python -m doc_validator.interface.cli_main
```

You should see:
```
✓ Drive credentials loaded
Authenticating with Google Drive API...
✓ Authentication successful
```

### Security Notes

- **Never commit** `bin/link.txt` to version control
- Keep your API key confidential
- Consider using API key restrictions
- Rotate keys regularly for production use

For more secure authentication (OAuth2), see [Advanced Google Drive Setup](GOOGLE_DRIVE_SETUP.md).

---

## Verification

### Verify Core Installation

```bash
# Check Python version
python --version  # or python3 --version

# Check pip
pip --version  # or pip3 --version

# List installed packages
pip list | grep -E "pandas|openpyxl|PyQt6"
```

Expected output:
```
openpyxl                  3.x.x
pandas                    1.5.x
PyQt6                     6.x.x
```

### Run Tests

```bash
# Run validation tests
python -m doc_validator.tests.test_validators

# Run real-world data tests
python -m doc_validator.tests.test_real_world_data
```

Expected output:
```
==============================================================
PASSED: 45
FAILED: 0
==============================================================
🎉 ALL TESTS PASSED!
```

### Test with Sample File

1. Create `INPUT` folder
2. Place a test Excel file there
3. Run:
   ```bash
   python -m doc_validator.tools.process_local_batch ./INPUT
   ```

---

## Troubleshooting

### Import Errors

**Error: "No module named 'pandas'"**
```bash
pip install pandas openpyxl
```

**Error: "No module named 'PyQt6'"**
```bash
pip install PyQt6
```

### GUI Issues

**Error: "Could not find the Qt platform plugin"**

Linux:
```bash
sudo apt install libxcb-xinerama0 libxcb-cursor0
```

Windows: Reinstall PyQt6
```cmd
pip uninstall PyQt6
pip install PyQt6
```

### Permission Errors

**Windows**: Run Command Prompt as Administrator

**macOS/Linux**: Use `--user` flag
```bash
pip install --user -r requirements.txt
```

Or use virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Python Version Issues

**Multiple Python versions installed**

Use specific version:
```bash
python3.10 -m pip install -r requirements.txt
python3.10 run_gui.py
```

Or create alias:
```bash
alias python=python3.10
```

### Network/Proxy Issues

If behind a corporate proxy:
```bash
pip install --proxy http://proxy.example.com:8080 -r requirements.txt
```

Or set environment variables:
```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

### Disk Space Issues

Check available space:
```bash
# Linux/macOS
df -h

# Windows
dir
```

Clean pip cache if needed:
```bash
pip cache purge
```

---

## Uninstallation

### Remove Python Packages

```bash
pip uninstall -y -r requirements.txt
pip uninstall -y -r requirements-gui.txt
```

### Remove Application

**Linux/macOS**:
```bash
rm -rf /path/to/amos-validator
```

**Windows**:
Delete the application folder.

### Remove Configuration

Delete these folders if they exist:
- `DATA/` - Output files
- `INPUT/` - Input files
- `bin/link.txt` - Credentials
- `__pycache__/` - Python cache

---

## Next Steps

After successful installation:

1. Read the [User Guide](USER_GUIDE.md)
2. Review [Validation Rules](VALIDATION_RULES.md)
3. Try processing a sample file
4. Configure Google Drive (if needed)
5. Set up your workflow

---

## Getting Help

- **Installation Issues**: [GitHub Issues](https://github.com/yourusername/amos-validator/issues)
- **General Questions**: [GitHub Discussions](https://github.com/yourusername/amos-validator/discussions)
- **Documentation**: Check other docs in `docs/` folder