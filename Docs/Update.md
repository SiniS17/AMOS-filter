# Auto-Update Implementation Plan for Python + PyInstaller Application

**Project:** AMOS Document Validator  
**Current Version:** BETA v1.25  
**Implementation Approach:** GitHub Releases (Recommended)

---

## 🎯 Overview

Your application is a PyQt6-based GUI tool with CLI support, distributed as a PyInstaller executable. The best approach is a **hybrid solution** that checks for updates and downloads new versions automatically.

---

## 📋 Plan Summary

### Option 1: GitHub Releases (Recommended) ✅
- ✅ Free hosting
- ✅ Version control integration
- ✅ Professional approach
- ✅ Easy to automate with GitHub Actions

### Option 2: Google Drive
- ✅ Already familiar (you use it for data)
- ✅ Simple setup
- ⚠️ Less professional
- ⚠️ Manual upload process

**Decision: Use GitHub Releases** since you already upload to GitHub.

---

## 🏗️ Implementation Architecture

```
doc_validator/
├── updater/
│   ├── __init__.py
│   ├── version.py           # Version management
│   ├── github_updater.py    # GitHub release checker
│   ├── downloader.py        # Download manager
│   └── installer.py         # Update installer
├── interface/
│   └── dialogs/
│       └── update_dialog.py # Update notification UI
└── config.py                # Add version info
```

---

## 📝 Detailed Implementation Steps

### **Phase 1: Version Management** (Day 1)

**Goal:** Create version tracking system and make it accessible throughout the app.

#### 1.1 Create Version Module
```python
# doc_validator/updater/version.py
"""
Version management for auto-updates.
"""
from dataclasses import dataclass
from typing import Optional

__version__ = "1.0.0"  # Current version

@dataclass
class Version:
    major: int
    minor: int
    patch: int
    
    @classmethod
    def from_string(cls, version_str: str):
        """Parse version string like '1.2.3'"""
        parts = version_str.strip().lstrip('v').split('.')
        return cls(
            major=int(parts[0]),
            minor=int(parts[1]) if len(parts) > 1 else 0,
            patch=int(parts[2]) if len(parts) > 2 else 0
        )
    
    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def __lt__(self, other):
        return (self.major, self.minor, self.patch) < \
               (other.major, other.minor, other.patch)

def get_current_version() -> Version:
    """Get current application version"""
    return Version.from_string(__version__)
```

#### 1.2 Update config.py
```python
# Add to doc_validator/config.py
from doc_validator.updater.version import __version__

APP_VERSION = __version__
UPDATE_CHECK_URL = "https://api.github.com/repos/YOUR_USERNAME/YOUR_REPO/releases/latest"
```

#### 1.3 Update MainWindow to show version
```python
# In doc_validator/interface/main_window.py
# Update the version label to use the actual version:

from doc_validator.updater.version import __version__

# Replace:
version_label = QLabel("BETA v1.25")
# With:
version_label = QLabel(f"BETA v{__version__}")
```

**Deliverables:**
- [ ] `doc_validator/updater/__init__.py` created
- [ ] `doc_validator/updater/version.py` created
- [ ] `config.py` updated with version info
- [ ] MainWindow shows dynamic version number

---

### **Phase 2: GitHub Release Checker** (Day 1-2)

**Goal:** Create a background checker that queries GitHub API for new releases.

#### 2.1 Create GitHub Updater
```python
# doc_validator/updater/github_updater.py
"""
Check for updates from GitHub releases.
"""
import requests
from typing import Optional, Tuple
from pathlib import Path

from .version import Version, get_current_version

class UpdateInfo:
    def __init__(self, version: Version, download_url: str, 
                 changelog: str, release_date: str):
        self.version = version
        self.download_url = download_url
        self.changelog = changelog
        self.release_date = release_date

class GitHubUpdateChecker:
    def __init__(self, repo_owner: str, repo_name: str):
        self.api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    
    def check_for_updates(self) -> Optional[UpdateInfo]:
        """
        Check if a new version is available.
        Returns UpdateInfo if update available, None otherwise.
        """
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            latest_version = Version.from_string(data['tag_name'])
            current_version = get_current_version()
            
            if latest_version > current_version:
                # Find Windows executable in assets
                download_url = None
                for asset in data.get('assets', []):
                    if asset['name'].endswith('.exe'):
                        download_url = asset['browser_download_url']
                        break
                
                if download_url:
                    return UpdateInfo(
                        version=latest_version,
                        download_url=download_url,
                        changelog=data.get('body', 'No changelog available'),
                        release_date=data.get('published_at', '')
                    )
            
            return None
            
        except Exception as e:
            print(f"Update check failed: {e}")
            return None
```

**Deliverables:**
- [ ] `doc_validator/updater/github_updater.py` created
- [ ] UpdateInfo class for storing release data
- [ ] GitHubUpdateChecker with check_for_updates() method
- [ ] Error handling for network issues

---

### **Phase 3: Download Manager** (Day 2)

**Goal:** Download update files with progress reporting.

#### 3.1 Create Downloader with Progress
```python
# doc_validator/updater/downloader.py
"""
Download manager for update files.
"""
import requests
from pathlib import Path
from typing import Callable, Optional

class DownloadProgress:
    def __init__(self, callback: Optional[Callable[[int, int], None]] = None):
        self.callback = callback
    
    def report(self, downloaded: int, total: int):
        if self.callback:
            self.callback(downloaded, total)

class Downloader:
    @staticmethod
    def download_file(url: str, destination: Path, 
                     progress: Optional[DownloadProgress] = None) -> bool:
        """
        Download file with progress reporting.
        """
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress:
                            progress.report(downloaded, total_size)
            
            return True
            
        except Exception as e:
            print(f"Download failed: {e}")
            if destination.exists():
                destination.unlink()
            return False
```

**Deliverables:**
- [ ] `doc_validator/updater/downloader.py` created
- [ ] DownloadProgress class for callbacks
- [ ] Downloader.download_file() with streaming
- [ ] Progress reporting via callback
- [ ] Error handling and cleanup

---

### **Phase 4: Update Installer** (Day 2-3)

**Goal:** Replace the running executable with the new version.

#### 4.1 Create Update Installer
```python
# doc_validator/updater/installer.py
"""
Install updates by replacing the executable.
"""
import sys
import subprocess
from pathlib import Path
import tempfile

class UpdateInstaller:
    @staticmethod
    def install_update(new_exe_path: Path) -> bool:
        """
        Install update by creating a batch script that:
        1. Waits for current app to close
        2. Replaces old exe with new exe
        3. Restarts the app
        4. Cleans up
        """
        if not getattr(sys, 'frozen', False):
            print("Cannot install updates in development mode")
            return False
        
        current_exe = Path(sys.executable)
        backup_exe = current_exe.with_suffix('.exe.old')
        
        # Create batch script
        batch_script = f"""@echo off
echo Installing update...
timeout /t 3 /nobreak > NUL

REM Backup old version
if exist "{backup_exe}" del "{backup_exe}"
move "{current_exe}" "{backup_exe}"

REM Install new version
move "{new_exe_path}" "{current_exe}"

REM Start new version
start "" "{current_exe}"

REM Clean up
timeout /t 2 /nobreak > NUL
if exist "{backup_exe}" del "{backup_exe}"
del "%~f0"
"""
        
        # Save batch script
        batch_file = Path(tempfile.gettempdir()) / "update_installer.bat"
        batch_file.write_text(batch_script, encoding='utf-8')
        
        # Run batch script and exit
        subprocess.Popen(
            [str(batch_file)],
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        return True
```

**Deliverables:**
- [ ] `doc_validator/updater/installer.py` created
- [ ] Batch script generation for Windows
- [ ] Backup mechanism for old version
- [ ] Silent background execution
- [ ] Auto-restart after update

---

### **Phase 5: GUI Integration** (Day 3-4)

**Goal:** Add update notifications and download UI to the application.

#### 5.1 Create Update Dialog
```python
# doc_validator/interface/dialogs/update_dialog.py
"""
Update notification dialog with download progress.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QProgressBar, QTextEdit
)
from PyQt6.QtCore import QThread, pyqtSignal
import sys

from doc_validator.updater.github_updater import UpdateInfo
from doc_validator.updater.downloader import Downloader, DownloadProgress

class DownloadThread(QThread):
    progress = pyqtSignal(int, int)  # downloaded, total
    finished = pyqtSignal(bool, str)  # success, file_path
    
    def __init__(self, download_url: str, destination: str):
        super().__init__()
        self.download_url = download_url
        self.destination = destination
    
    def run(self):
        from pathlib import Path
        
        dest_path = Path(self.destination)
        progress_callback = DownloadProgress(
            callback=lambda d, t: self.progress.emit(d, t)
        )
        
        success = Downloader.download_file(
            self.download_url,
            dest_path,
            progress_callback
        )
        
        self.finished.emit(success, str(dest_path) if success else "")

class UpdateDialog(QDialog):
    def __init__(self, update_info: UpdateInfo, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.download_thread = None
        self.downloaded_file = None
        
        self.setWindowTitle("Update Available")
        self.setMinimumSize(500, 400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(f"New Version Available: {self.update_info.version}")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Changelog
        changelog_label = QLabel("What's New:")
        layout.addWidget(changelog_label)
        
        changelog = QTextEdit()
        changelog.setReadOnly(True)
        changelog.setPlainText(self.update_info.changelog)
        changelog.setMaximumHeight(200)
        layout.addWidget(changelog)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.btn_download = QPushButton("Download and Install")
        self.btn_download.clicked.connect(self.start_download)
        button_layout.addWidget(self.btn_download)
        
        self.btn_later = QPushButton("Remind Me Later")
        self.btn_later.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_later)
        
        layout.addLayout(button_layout)
    
    def start_download(self):
        import tempfile
        from pathlib import Path
        
        self.btn_download.setEnabled(False)
        self.progress_bar.show()
        
        # Download to temp location
        temp_dir = Path(tempfile.gettempdir())
        dest = temp_dir / f"DocumentValidator_{self.update_info.version}.exe"
        
        self.download_thread = DownloadThread(
            self.update_info.download_url,
            str(dest)
        )
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.start()
    
    def update_progress(self, downloaded: int, total: int):
        if total > 0:
            percent = int((downloaded / total) * 100)
            self.progress_bar.setValue(percent)
    
    def download_finished(self, success: bool, file_path: str):
        if success:
            self.downloaded_file = file_path
            self.btn_download.setText("Install Now")
            self.btn_download.clicked.disconnect()
            self.btn_download.clicked.connect(self.install_update)
            self.btn_download.setEnabled(True)
        else:
            self.btn_download.setText("Download Failed - Retry")
            self.btn_download.setEnabled(True)
    
    def install_update(self):
        from pathlib import Path
        from doc_validator.updater.installer import UpdateInstaller
        from PyQt6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            "Install Update",
            "The application will close and restart to install the update.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if UpdateInstaller.install_update(Path(self.downloaded_file)):
                sys.exit(0)  # Exit app - batch script will restart
```

#### 5.2 Integrate into MainWindow
```python
# Add to doc_validator/interface/main_window.py

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox
from doc_validator.updater.github_updater import GitHubUpdateChecker
from doc_validator.interface.dialogs.update_dialog import UpdateDialog

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # ... existing code ...
        
        # Check for updates on startup (in background, after 2 seconds)
        QTimer.singleShot(2000, self.check_for_updates)
    
    def check_for_updates(self, silent=True):
        """Check for updates (silent=True means no dialog if up to date)"""
        # TODO: Replace with your actual GitHub username and repo name
        checker = GitHubUpdateChecker("YOUR_USERNAME", "YOUR_REPO")
        update_info = checker.check_for_updates()
        
        if update_info:
            dialog = UpdateDialog(update_info, self)
            dialog.exec()
        elif not silent:
            QMessageBox.information(
                self,
                "No Updates",
                "You are running the latest version."
            )
```

**Deliverables:**
- [ ] `doc_validator/interface/dialogs/__init__.py` created
- [ ] `doc_validator/interface/dialogs/update_dialog.py` created
- [ ] UpdateDialog with changelog display
- [ ] DownloadThread for background downloading
- [ ] Progress bar integration
- [ ] MainWindow integration with QTimer
- [ ] Manual "Check for Updates" menu option (optional)

---

### **Phase 6: GitHub Release Automation** (Day 4)

**Goal:** Automate building and releasing new versions.

#### 6.1 Create GitHub Actions Workflow
```yaml
# .github/workflows/release.yml
name: Build and Release

on:
  push:
    tags:
      - 'v*'  # Trigger on version tags like v1.0.0

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build executable
      run: |
        pyinstaller --name="DocumentValidator" --onefile --windowed --icon=doc_validator/resources/icons/app_logo.ico run_gui.py
    
    - name: Create Release
      uses: softprops/action-gh-release@v1
      with:
        files: dist/DocumentValidator.exe
        body_path: CHANGELOG.md
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

#### 6.2 Create CHANGELOG.md Template
```markdown
# Changelog

## [1.1.0] - 2025-01-XX

### Added
- Auto-update functionality
- Check for updates on startup
- Download and install updates from GitHub

### Fixed
- Bug fixes

### Changed
- Improvements
```

**Deliverables:**
- [ ] `.github/workflows/release.yml` created
- [ ] `CHANGELOG.md` created
- [ ] GitHub Actions tested with a tag push
- [ ] Release appears on GitHub with .exe attached

---

### **Phase 7: Settings & Preferences** (Day 5) - OPTIONAL

**Goal:** Let users control update behavior.

#### 7.1 Add Update Settings
```python
# Add to a new settings module or MainWindow

class UpdateSettings:
    def __init__(self):
        self.check_on_startup = True
        self.auto_download = False  # Ask before downloading
        self.check_interval_days = 1
        self.last_check_date = None
    
    def should_check_updates(self) -> bool:
        """Check if enough time has passed since last check"""
        from datetime import datetime, timedelta
        
        if not self.check_on_startup:
            return False
        
        if not self.last_check_date:
            return True
        
        elapsed = datetime.now() - self.last_check_date
        return elapsed.days >= self.check_interval_days
    
    def mark_checked(self):
        """Update last check timestamp"""
        from datetime import datetime
        self.last_check_date = datetime.now()
```

**Deliverables (Optional):**
- [ ] Settings class for update preferences
- [ ] Settings UI in MainWindow
- [ ] Persistent settings storage (JSON/INI file)
- [ ] "Check for updates on startup" checkbox

---

## 🚀 Deployment Process

### Step-by-Step Release Process:

1. **Update Version Number**
   ```python
   # doc_validator/updater/version.py
   __version__ = "1.1.0"  # Increment version
   ```

2. **Update CHANGELOG.md**
   - Document new features
   - List bug fixes
   - Note any breaking changes

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "Release v1.1.0: Add auto-update feature"
   ```

4. **Create and Push Tag**
   ```bash
   git tag v1.1.0
   git push origin main
   git push origin v1.1.0
   ```

5. **GitHub Actions automatically:**
   - Builds the executable
   - Creates a GitHub Release
   - Uploads the .exe file
   - Users get notified on next launch!

---

## 🧪 Testing Plan

### Manual Testing Checklist:

- [ ] Version detection works correctly
- [ ] Update check doesn't block UI (happens in background)
- [ ] Update dialog shows correctly with changelog
- [ ] Download shows progress
- [ ] Download can be cancelled
- [ ] Update installs without errors
- [ ] App restarts successfully after update
- [ ] Old version is backed up
- [ ] Network errors are handled gracefully
- [ ] "No update available" case works
- [ ] Settings are preserved after update
- [ ] Works in development mode (skips install)
- [ ] Works in frozen/exe mode

### Test Scenarios:

1. **Simulated Update Test:**
   - Temporarily set current version to 0.9.0
   - Create a GitHub release for 1.0.0
   - Verify update flow works end-to-end

2. **Network Failure Test:**
   - Disconnect internet
   - Verify graceful failure message
   - Verify app still works normally

3. **Partial Download Test:**
   - Interrupt download (close dialog)
   - Verify cleanup happens
   - Verify retry works

4. **Multiple Updates:**
   - Test updating from v1.0.0 → v1.1.0 → v1.2.0
   - Verify each step works

---

## 📦 Alternative: Simple Update Notification

If full auto-update is too complex initially, start with **update notification only**:

```python
# Simpler approach - just notify users and open browser
class SimpleUpdateChecker:
    def check_and_notify(self):
        update_info = self.check_for_updates()
        if update_info:
            reply = QMessageBox.information(
                None,
                "Update Available",
                f"Version {update_info.version} is available!\n\n"
                f"Click 'Open' to download from GitHub.",
                QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Later
            )
            
            if reply == QMessageBox.StandardButton.Open:
                import webbrowser
                webbrowser.open(update_info.download_url)
```

This is a **good first step** before implementing full auto-install.

---

## 🎯 Implementation Timeline

| Phase | Task | Duration | Status |
|-------|------|----------|--------|
| 1 | Version management | 2-3 hours | ⬜ Not started |
| 2 | GitHub checker | 3-4 hours | ⬜ Not started |
| 3 | Download manager | 2-3 hours | ⬜ Not started |
| 4 | Update installer | 4-5 hours | ⬜ Not started |
| 5 | GUI integration | 3-4 hours | ⬜ Not started |
| 6 | GitHub Actions | 2-3 hours | ⬜ Not started |
| 7 | Testing | 4-5 hours | ⬜ Not started |
| **Total** | **Complete implementation** | **~2-3 days** | |

---

## 🔐 Security Considerations

1. **Verify Downloads (Future Enhancement):**
   ```python
   import hashlib
   
   def verify_checksum(file_path, expected_hash):
       sha256 = hashlib.sha256()
       with open(file_path, 'rb') as f:
           for chunk in iter(lambda: f.read(4096), b""):
               sha256.update(chunk)
       return sha256.hexdigest() == expected_hash
   ```

2. **HTTPS Only:** ✅ Already handled by GitHub

3. **Code Signing (Optional):** Consider signing your .exe files
   - Increases user trust
   - Prevents Windows SmartScreen warnings
   - Costs money (~$100-300/year for certificate)

---

## 📚 Additional Resources

- **PyInstaller Documentation:** https://pyinstaller.org/
- **GitHub Releases API:** https://docs.github.com/en/rest/releases
- **PyQt6 QThread:** https://doc.qt.io/qtforpython-6/PySide6/QtCore/QThread.html
- **GitHub Actions for Python:** https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python

---

## 🚦 Current Status

**Phase:** Planning  
**Next Step:** Phase 1 - Version Management

Ready to start implementation? Let's work through this phase by phase! 🚀

---

## 📝 Notes

- Remember to replace `YOUR_USERNAME` and `YOUR_REPO` with actual values
- Test each phase thoroughly before moving to the next
- Keep backups of working versions
- Document any issues or deviations from the plan
- Update this document as you progress