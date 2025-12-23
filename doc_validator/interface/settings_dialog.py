# doc_validator/interface/settings_dialog.py
"""
Settings dialog for AMOS Documentation Validator.
"""

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QLineEdit,
    QGroupBox,
    QCheckBox,
    QFileDialog,
    QDialogButtonBox,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
)

from doc_validator.interface.settings_manager import SettingsManager


class SettingsDialog(QDialog):
    """Settings dialog with tabs for different setting categories."""

    settings_changed = pyqtSignal()  # Emitted when settings are saved

    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings = settings_manager
        self.setWindowTitle("Settings")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        self._setup_ui()
        self._load_current_settings()

    def _setup_ui(self):
        """Build the settings UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title
        title = QLabel("⚙️ Application Settings")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2196F3;
            padding: 10px;
        """)
        layout.addWidget(title)

        # Input Source Section
        input_group = self._create_input_source_section()
        layout.addWidget(input_group)

        # SEQ Auto-Valid Section
        seq_group = self._create_seq_section()
        layout.addWidget(seq_group)

        layout.addStretch()

        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )
        button_box.accepted.connect(self._save_and_close)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(
            self._restore_defaults
        )
        layout.addWidget(button_box)

        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                color: #e0e0e0;
            }
            QGroupBox {
                border: 2px solid #444;
                border-radius: 8px;
                margin-top: 12px;
                padding: 15px 10px 10px 10px;
                background-color: #2a2a2a;
                font-weight: bold;
                color: #2196F3;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 2px solid #444;
                border-radius: 5px;
                padding: 6px 12px;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #333;
                border-color: #2196F3;
            }
            QComboBox {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 2px solid #444;
                border-radius: 5px;
                padding: 6px 8px;
            }
            QLineEdit {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 2px solid #444;
                border-radius: 5px;
                padding: 6px 8px;
            }
            QListWidget {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 2px solid #444;
                border-radius: 5px;
            }
            QCheckBox {
                color: #e0e0e0;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #666;
                border-radius: 4px;
                background-color: #2a2a2a;
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border-color: #2196F3;
            }
        """)

    def _create_input_source_section(self) -> QGroupBox:
        """Create input source settings section."""
        group = QGroupBox("📂 Input Source")
        layout = QVBoxLayout()

        # Source type selector
        source_row = QHBoxLayout()
        source_row.addWidget(QLabel("Load files from:"))

        self.combo_source = QComboBox()
        self.combo_source.addItem("📁 Local Folder (INPUT)", "local")
        self.combo_source.addItem("☁️  Google Drive", "drive")
        self.combo_source.currentIndexChanged.connect(self._on_source_changed)
        source_row.addWidget(self.combo_source)
        source_row.addStretch()

        layout.addLayout(source_row)

        # Local folder path
        path_row = QHBoxLayout()
        path_row.addWidget(QLabel("Local folder:"))

        self.line_local_path = QLineEdit()
        self.line_local_path.setPlaceholderText("Path to local INPUT folder...")
        path_row.addWidget(self.line_local_path, 1)

        self.btn_browse = QPushButton("Browse...")
        self.btn_browse.clicked.connect(self._browse_folder)
        path_row.addWidget(self.btn_browse)

        layout.addLayout(path_row)

        # Drive info
        self.label_drive_info = QLabel("☁️  Using configured Google Drive folder from credentials file")
        self.label_drive_info.setStyleSheet("color: #4CAF50; font-style: italic; padding: 5px;")
        layout.addWidget(self.label_drive_info)

        group.setLayout(layout)
        return group

    def _create_seq_section(self) -> QGroupBox:
        """Create SEQ auto-valid patterns section."""
        group = QGroupBox("✓ SEQ Auto-Valid Patterns")
        layout = QVBoxLayout()

        info = QLabel(
            "Select which SEQ patterns should be automatically marked as 'Valid' "
            "without checking references:"
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #888; font-size: 11px; font-weight: normal;")
        layout.addWidget(info)

        # Checkboxes for common patterns
        self.seq_checkboxes = {}
        patterns = [
            ("1.", "SEQ 1.x (e.g., 1.1, 1.2, 1.10)"),
            ("2.", "SEQ 2.x (e.g., 2.1, 2.2, 2.5)"),
            ("3.", "SEQ 3.x (e.g., 3.1, 3.2, 3.15)"),
            ("10.", "SEQ 10.x (e.g., 10.1, 10.2)"),
        ]

        for pattern, label in patterns:
            cb = QCheckBox(label)
            self.seq_checkboxes[pattern] = cb
            layout.addWidget(cb)

        group.setLayout(layout)
        return group

    def _on_source_changed(self, index: int):
        """Handle source type change."""
        source_type = self.combo_source.currentData()

        if source_type == "local":
            self.line_local_path.setEnabled(True)
            self.btn_browse.setEnabled(True)
            self.label_drive_info.hide()
        else:
            self.line_local_path.setEnabled(False)
            self.btn_browse.setEnabled(False)
            self.label_drive_info.show()

    def _browse_folder(self):
        """Browse for local folder."""
        current = self.line_local_path.text()
        if not current:
            from doc_validator.config import INPUT_FOLDER
            current = INPUT_FOLDER

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Input Folder",
            current,
            QFileDialog.Option.ShowDirsOnly
        )

        if folder:
            self.line_local_path.setText(folder)

    def _load_current_settings(self):
        """Load current settings into UI."""
        from doc_validator.config import INPUT_FOLDER

        # Input source
        source_type = self.settings.get("input_source_type", "local")
        index = self.combo_source.findData(source_type)
        if index >= 0:
            self.combo_source.setCurrentIndex(index)

        # Local path - ensure it's never empty
        local_path = self.settings.get("input_local_path", INPUT_FOLDER)
        if not local_path:
            local_path = INPUT_FOLDER
        self.line_local_path.setText(local_path)

        # SEQ patterns
        patterns = self.settings.get("seq_auto_valid_patterns", ["1.", "2.", "3.", "10."])
        for pattern, checkbox in self.seq_checkboxes.items():
            checkbox.setChecked(pattern in patterns)

        # Update UI based on source type
        self._on_source_changed(0)

    def _save_and_close(self):
        """Save settings and close dialog."""
        from doc_validator.config import INPUT_FOLDER

        # Save input source
        source_type = self.combo_source.currentData()
        self.settings.set("input_source_type", source_type)

        # Save local path - ensure it's never empty
        local_path = self.line_local_path.text().strip()
        if not local_path:
            local_path = INPUT_FOLDER
        self.settings.set("input_local_path", local_path)

        # Save SEQ patterns
        patterns = [
            pattern for pattern, cb in self.seq_checkboxes.items()
            if cb.isChecked()
        ]
        self.settings.set("seq_auto_valid_patterns", patterns)

        # Emit signal
        self.settings_changed.emit()

        self.accept()

    def _restore_defaults(self):
        """Restore default settings."""
        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "Are you sure you want to restore all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.settings.reset_to_defaults()
            self._load_current_settings()
            QMessageBox.information(
                self,
                "Restored",
                "Settings have been restored to defaults."
            )