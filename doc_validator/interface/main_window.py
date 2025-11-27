from __future__ import annotations

import os
import sys
import subprocess
import platform
from typing import List, Optional
from datetime import date

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QMessageBox,
    QHeaderView,
)

from doc_validator.config import LINK_FILE
from doc_validator.core.drive_io import (
    authenticate_drive_api,
    get_all_excel_files_from_folder,
    read_credentials_file,
)

from doc_validator.interface.panels.date_filter_panel import DateFilterPanel
from doc_validator.interface.workers.processing_worker import (
    ProcessingWorker,
    DriveFileInfo,
)


class MainWindow(QMainWindow):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.setWindowTitle("AMOSFilter - Documentation Validator")
        self.resize(1000, 700)

        # Credentials / Drive folder info
        self.api_key: Optional[str] = None
        self.folder_id: Optional[str] = None
        self.drive_files: List[DriveFileInfo] = []

        # Worker thread reference
        self.worker: Optional[ProcessingWorker] = None

        # Build UI
        self._setup_ui()

        # Load Drive file list on startup
        self._load_drive_files()

    # ---------------------- UI Setup ----------------------

    def _setup_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)

        main_layout = QVBoxLayout()
        central.setLayout(main_layout)

        # ========== TOP TOOLBAR ==========
        toolbar_layout = QHBoxLayout()

        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.setToolTip("Refresh file list from Google Drive")
        self.btn_refresh.clicked.connect(self._load_drive_files)

        self.btn_open_folder = QPushButton("📁 Open Output Folder")
        self.btn_open_folder.setToolTip("Open the DATA folder (root output directory)")
        self.btn_open_folder.clicked.connect(self._open_output_folder)

        toolbar_layout.addWidget(self.btn_refresh)
        toolbar_layout.addWidget(self.btn_open_folder)
        toolbar_layout.addStretch()

        main_layout.addLayout(toolbar_layout)

        # ========== DATE FILTER SECTION ==========
        self.date_filter_panel = DateFilterPanel(self)
        main_layout.addWidget(self.date_filter_panel)

        # ========== FILE LIST SECTION ==========
        file_section_label = QLabel("Excel files in configured Google Drive folder:")
        file_section_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        main_layout.addWidget(file_section_label)

        # Table of files
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Process?", "File Name"])
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        # Enhanced style with checkmark
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #3b3b3b;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #666;
                border-radius: 4px;
                background-color: #2b2b2b;
            }
            QTableWidget::indicator:unchecked {
                background-color: #2b2b2b;
                border: 2px solid #666;
            }
            QTableWidget::indicator:unchecked:hover {
                background-color: #3b3b3b;
                border: 2px solid #999;
            }
            QTableWidget::indicator:checked {
                background-color: #2196F3;
                border: 2px solid #2196F3;
            }
            QTableWidget::indicator:checked:hover {
                background-color: #42A5F5;
                border: 2px solid #42A5F5;
            }
        """)

        main_layout.addWidget(self.table)

        # Buttons under table
        btn_layout = QHBoxLayout()
        self.btn_select_all = QPushButton("Select All")
        self.btn_select_all.clicked.connect(self._select_all)

        self.btn_deselect_all = QPushButton("Deselect All")
        self.btn_deselect_all.clicked.connect(self._deselect_all)

        self.btn_run = QPushButton("▶ Run")
        self.btn_run.setStyleSheet("font-weight: bold; font-size: 13px;")
        self.btn_run.clicked.connect(self._on_run_clicked)

        btn_layout.addWidget(self.btn_select_all)
        btn_layout.addWidget(self.btn_deselect_all)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_run)

        main_layout.addLayout(btn_layout)

        # ========== PROGRESS SECTION (NEW) ==========
        from PyQt6.QtWidgets import QProgressBar

        # Progress container (hidden by default)
        self.progress_container = QWidget()
        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(0, 5, 0, 5)
        self.progress_container.setLayout(progress_layout)

        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        progress_layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)

        self.progress_container.hide()  # Hidden by default
        main_layout.addWidget(self.progress_container)

        # ========== CONSOLE OUTPUT ==========
        console_header = QHBoxLayout()
        console_label = QLabel("Console Output:")
        console_label.setStyleSheet("font-weight: bold; margin-top: 8px;")

        self.btn_toggle_console = QPushButton("▼ Collapse")
        self.btn_toggle_console.setMaximumWidth(100)
        self.btn_toggle_console.clicked.connect(self._toggle_console)

        console_header.addWidget(console_label)
        console_header.addStretch()
        console_header.addWidget(self.btn_toggle_console)

        main_layout.addLayout(console_header)

        # Console-style log output
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.log_text.setStyleSheet(
            "font-family: Consolas, 'Courier New', monospace; font-size: 11px;"
        )
        self.log_text.setMaximumHeight(200)
        main_layout.addWidget(self.log_text)

    # ---------------------- Console Toggle ----------------------

    def _toggle_console(self) -> None:
        """Toggle console visibility."""
        if self.log_text.isVisible():
            self.log_text.hide()
            self.btn_toggle_console.setText("▲ Expand")
        else:
            self.log_text.show()
            self.btn_toggle_console.setText("▼ Collapse")

    # ---------------------- Helpers ----------------------

    def _append_log(self, text: str) -> None:
        """Append text to log window and scroll to bottom."""
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
        self.log_text.insertPlainText(text)
        self.log_text.moveCursor(QTextCursor.MoveOperation.End)

    # ---------------------- Drive Loading ----------------------

    def _load_drive_files(self) -> None:
        """Read credentials and list all Excel files in the configured folder."""
        self._append_log(f"🔄 Reading credentials from: {LINK_FILE}\n")
        api_key, folder_id = read_credentials_file(LINK_FILE)

        if not api_key or not folder_id:
            self._append_log(
                "❌ ERROR: Invalid credentials (GG_API_KEY or GG_FOLDER_ID missing).\n"
            )
            QMessageBox.critical(
                self,
                "Credentials Error",
                f"Could not read GG_API_KEY and GG_FOLDER_ID from:\n{LINK_FILE}",
            )
            self.btn_run.setEnabled(False)
            return

        self.api_key = api_key
        self.folder_id = folder_id

        try:
            self._append_log("🔐 Authenticating with Google Drive API...\n")
            drive_service = authenticate_drive_api(self.api_key)
            self._append_log("✓ Authentication successful.\n")
            self._append_log(
                "📂 Fetching Excel file list from configured folder...\n"
            )

            self.drive_files = [
                DriveFileInfo(
                    file_id=f["id"],
                    name=f["name"],
                    mime_type=f.get("mimeType", ""),
                )
                for f in get_all_excel_files_from_folder(drive_service, self.folder_id)
            ]

            self._append_log(
                f"✓ Found {len(self.drive_files)} Excel file(s) in the folder.\n"
            )
            self._populate_table()

        except Exception as e:  # defensive
            import traceback

            self._append_log(f"\n✗ ERROR while loading Drive files: {e!r}\n")
            self._append_log(traceback.format_exc())
            QMessageBox.critical(
                self,
                "Drive Error",
                f"Could not load files from Google Drive:\n{e}",
            )

    def _populate_table(self) -> None:
        self.table.setRowCount(0)

        for row_idx, file_info in enumerate(self.drive_files):
            self.table.insertRow(row_idx)

            # Checkbox item - centered and styled for dark mode
            chk_item = QTableWidgetItem()
            chk_item.setFlags(
                Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsEnabled
            )
            chk_item.setCheckState(Qt.CheckState.Unchecked)
            chk_item.setText("")  # Remove any text
            chk_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the checkbox
            self.table.setItem(row_idx, 0, chk_item)

            name_item = QTableWidgetItem(file_info.name)
            self.table.setItem(row_idx, 1, name_item)

        self.table.resizeRowsToContents()

    # ---------------------- Selection Helpers ----------------------

    def _select_all(self) -> None:
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item is not None:
                item.setCheckState(Qt.CheckState.Checked)

    def _deselect_all(self) -> None:
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item is not None:
                item.setCheckState(Qt.CheckState.Unchecked)

    # ---------------------- Open Output Folder ----------------------

    def _open_output_folder(self) -> None:
        from doc_validator.config import DATA_FOLDER

        if not os.path.isdir(DATA_FOLDER):
            QMessageBox.warning(
                self,
                "No Output Folder",
                f"DATA folder does not exist yet:\n{DATA_FOLDER}",
            )
            return

        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(DATA_FOLDER)
            elif system == "Darwin":  # macOS
                subprocess.Popen(["open", DATA_FOLDER])
            else:  # Linux
                subprocess.Popen(["xdg-open", DATA_FOLDER])
        except Exception as e:  # defensive
            QMessageBox.critical(
                self,
                "Error Opening Folder",
                f"Could not open folder:\n{e}",
            )

    # ---------------------- Run Button / Worker ----------------------

    def _on_run_clicked(self) -> None:
        if not self.api_key or not self.folder_id:
            QMessageBox.critical(
                self,
                "Credentials Error",
                "Cannot run: API key or folder ID is not set.",
            )
            return

        selected_files: List[DriveFileInfo] = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                selected_files.append(self.drive_files[row])

        if not selected_files:
            QMessageBox.warning(
                self,
                "No Files Selected",
                "Please select at least one file to process.",
            )
            return

        # Disable Run button while processing
        self.btn_run.setEnabled(False)
        self.btn_refresh.setEnabled(False)

        # Get date filter settings from panel
        filter_start: Optional[date] = None
        filter_end: Optional[date] = None

        if self.date_filter_panel.is_enabled():
            try:
                filter_start, filter_end = self.date_filter_panel.get_range()
            except ValueError:
                QMessageBox.warning(
                    self,
                    "Invalid Date",
                    (
                        "Please enter dates as:\n"
                        "  - YYYY-MM-DD (e.g. 2025-11-27)\n"
                        "  - or relative: -1d, +2d, -1m, +1y"
                    ),
                )
                self.btn_run.setEnabled(True)
                self.btn_refresh.setEnabled(True)
                return

            self._append_log(
                f"\n📅 Date filter enabled:\n"
                f"   From: {filter_start}\n"
                f"   To: {filter_end}\n"
            )

        self._append_log(
            "\n" + "=" * 60 + "\n"
                              "▶ Starting processing of selected files...\n"
            + "=" * 60 + "\n"
        )

        # Show progress bar
        self.progress_container.show()
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting...")

        # Create and start worker thread
        self.worker = ProcessingWorker(
            api_key=self.api_key,
            folder_id=self.folder_id,
            selected_files=selected_files,
            filter_start_date=filter_start,
            filter_end_date=filter_end,
        )

        # Connect signals
        self.worker.log_message.connect(self._append_log)
        self.worker.progress_updated.connect(self._update_progress)
        self.worker.finished_with_results.connect(self._on_processing_finished)
        self.worker.finished.connect(self._on_worker_thread_finished)

        self.worker.start()

    def _on_worker_thread_finished(self) -> None:
        """Called when worker thread actually finishes (Qt's finished signal)."""
        # This ensures the thread is properly cleaned up
        if self.worker:
            self.worker.deleteLater()
            self.worker = None

    def _update_progress(self, value: int, status: str) -> None:
        """Update the embedded progress bar and label."""
        self.progress_bar.setValue(value)
        self.progress_label.setText(status)

    def _on_processing_finished(self, results: list) -> None:
        # Hide progress bar
        self.progress_container.hide()

        # Re-enable UI immediately
        self.btn_run.setEnabled(True)
        self.btn_refresh.setEnabled(True)

        # Summarize results
        success_count = sum(1 for r in results if r.get("output_file"))
        total = len(results)
        failed_count = total - success_count

        from doc_validator.config import DATA_FOLDER

        if success_count == total:
            msg = f"✓ All {total} file(s) processed successfully!"
        elif success_count > 0:
            msg = (
                f"⚠️ Processed {success_count}/{total} file(s) successfully.\n"
                f"{failed_count} file(s) failed."
            )
        else:
            msg = f"❌ All {total} file(s) failed to process."

        msg += f"\n\nOutput directory:\n{DATA_FOLDER}"

        # Show completion message
        QMessageBox.information(
            self,
            "Processing Complete",
            msg,
        )



def launch() -> None:
    """Launch the PyQt6 GUI."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Prevent app from quitting when last window closes (if you have hidden windows)
    app.setQuitOnLastWindowClosed(True)

    window = MainWindow()
    window.show()

    # Store reference to prevent garbage collection
    app.main_window = window

    sys.exit(app.exec())