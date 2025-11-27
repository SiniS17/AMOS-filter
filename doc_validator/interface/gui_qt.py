# doc_validator/interface/gui_qt.py
# Date filtering now handled in core pipeline - GUI just passes parameters

from __future__ import annotations
from PyQt6.QtGui import QTextCursor
import os
import sys
import subprocess
import platform
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QDate
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
    QProgressDialog,
    QDateEdit,
    QCheckBox,
    QGroupBox,
)

from doc_validator.config import LINK_FILE
from doc_validator.core.drive_io import (
    authenticate_drive_api,
    get_all_excel_files_from_folder,
    download_file_from_drive,
    read_credentials_file,
)
from doc_validator.core.excel_pipeline import process_excel
from datetime import date


# ---------------------------------------------------------------------
# Helper dataclass for Drive files
# ---------------------------------------------------------------------

@dataclass
class DriveFileInfo:
    file_id: str
    name: str
    mime_type: str


# ---------------------------------------------------------------------
# Stream redirection to show console output in the GUI
# ---------------------------------------------------------------------

class LogEmitter(QObject):
    message = pyqtSignal(str)


class EmittingStream:
    """
    A file-like stream that sends written text to a Qt signal.
    Used to capture print() output from existing code and mirror it
    into the GUI log window, while still printing to real stdout.
    """

    def __init__(self, emitter: LogEmitter, original_stream):
        self.emitter = emitter
        self.original_stream = original_stream

    def write(self, text: str):
        if text:
            # Emit to GUI
            self.emitter.message.emit(text)
            # Still write to original stdout/stderr (so IDE console works)
            if self.original_stream is not None:
                self.original_stream.write(text)

    def flush(self):
        if self.original_stream is not None:
            self.original_stream.flush()


# ---------------------------------------------------------------------
# Worker thread to process selected files
# ---------------------------------------------------------------------

class ProcessingWorker(QThread):
    log_message = pyqtSignal(str)
    progress_updated = pyqtSignal(int, str)  # percentage (0-100), status_text
    finished_with_results = pyqtSignal(list)

    def __init__(
            self,
            api_key: str,
            folder_id: str,
            selected_files: List[DriveFileInfo],
            filter_start_date: Optional[date] = None,
            filter_end_date: Optional[date] = None,
            parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.api_key = api_key
        self.folder_id = folder_id
        self.selected_files = selected_files
        self.filter_start_date = filter_start_date
        self.filter_end_date = filter_end_date
        self._cancelled = False
        self._line_count = 0
        self._estimated_lines_per_file = 50

    def cancel(self):
        """Request cancellation of processing."""
        self._cancelled = True

    def _emit_log_and_count(self, message: str):
        """Emit log message and update progress based on line count."""
        self.log_message.emit(message)

        # Count lines in message
        lines = message.count('\n') + (1 if message and not message.endswith('\n') else 0)
        self._line_count += lines

        # Calculate progress percentage
        total_files = len(self.selected_files)
        estimated_total_lines = total_files * self._estimated_lines_per_file
        progress = min(99, int((self._line_count / estimated_total_lines) * 100))

        # Extract status from message (first line, trimmed)
        status = message.split('\n')[0].strip()[:60] if message else "Processing..."

        self.progress_updated.emit(progress, status)

    def run(self):
        """
        Run in background thread:
        - authenticate
        - download each selected file
        - process it with process_excel (date filter handled in core!)
        - emit log messages with progress tracking
        """
        results: List[Dict[str, Any]] = []

        # Redirect stdout so all prints from process_excel()
        # also appear in the GUI log window.
        original_stdout = sys.stdout
        stream = EmittingStream(LogEmitter(), original_stdout)

        # Connect inner emitter to our counting log method
        stream.emitter.message.connect(self._emit_log_and_count)

        sys.stdout = stream

        try:
            self._emit_log_and_count("Authenticating with Google Drive API...\n")
            self.progress_updated.emit(5, "Authenticating...")

            drive_service = authenticate_drive_api(self.api_key)
            self._emit_log_and_count("✓ Authentication successful.\n\n")
            self.progress_updated.emit(10, "Authentication successful")

            total = len(self.selected_files)
            self._emit_log_and_count(
                f"Processing {total} selected file(s) from Drive folder...\n"
            )

            for idx, file_info in enumerate(self.selected_files, start=1):
                # Check for cancellation
                if self._cancelled:
                    self._emit_log_and_count("\n⚠️ Processing cancelled by user.\n")
                    break

                # Emit status update
                self.progress_updated.emit(
                    int(10 + (idx - 1) / total * 85),
                    f"[{idx}/{total}] {file_info.name}"
                )

                self._emit_log_and_count(
                    "\n" + "=" * 60 + "\n"
                                      f"[{idx}/{total}] {file_info.name}\n"
                    + "=" * 60 + "\n"
                )

                # Download to a temp GUI folder (under DATA/temp_gui)
                wp_placeholder = "temp_gui"
                local_path = download_file_from_drive(
                    drive_service,
                    file_info.file_id,
                    wp_placeholder,
                    file_info.name,
                )

                if not local_path:
                    self._emit_log_and_count(
                        f"✗ Failed to download file: {file_info.name}\n"
                    )
                    results.append(
                        {
                            "source_name": file_info.name,
                            "source_id": file_info.file_id,
                            "local_path": None,
                            "output_file": None,
                        }
                    )
                    continue

                self._emit_log_and_count(
                    f"Local file path: {local_path}\n"
                )

                # Run the Excel processing pipeline with date filter
                # (date filtering is now handled inside process_excel!)
                output_file = process_excel(
                    local_path,
                    filter_start_date=self.filter_start_date,
                    filter_end_date=self.filter_end_date,
                )

                if output_file:
                    self._emit_log_and_count(
                        f"✓ Processing finished for {file_info.name}\n"
                        f"  Output: {output_file}\n"
                    )
                else:
                    self._emit_log_and_count(
                        f"✗ Processing failed for {file_info.name}\n"
                    )

                results.append(
                    {
                        "source_name": file_info.name,
                        "source_id": file_info.file_id,
                        "local_path": local_path,
                        "output_file": output_file,
                    }
                )

            if not self._cancelled:
                self._emit_log_and_count("\n✓ All selected files have been processed.\n")
                self.progress_updated.emit(100, "Complete!")

        except Exception as e:
            # In case of unexpected error
            import traceback

            self._emit_log_and_count(f"\n✗ ERROR: {str(e)}\n")
            self._emit_log_and_count(traceback.format_exc())

        finally:
            # Restore stdout
            sys.stdout = original_stdout
            # Emit results back to GUI thread
            self.finished_with_results.emit(results)


# ---------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------

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

        # Progress dialog reference
        self.progress_dialog: Optional[QProgressDialog] = None

        # Date filter controls
        self.date_filter_enabled = False
        self.filter_start_date: Optional[date] = None
        self.filter_end_date: Optional[date] = None

        # Build UI
        self._setup_ui()

        # Load Drive file list on startup
        self._load_drive_files()

    # ---------------------- UI Setup ----------------------

    def _setup_ui(self):
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
        date_filter_group = QGroupBox("📅 Date Filter (Optional)")
        date_filter_layout = QVBoxLayout()

        # Checkbox to enable/disable filter
        self.chk_enable_filter = QCheckBox("Enable date filtering")
        self.chk_enable_filter.stateChanged.connect(self._toggle_date_filter)
        date_filter_layout.addWidget(self.chk_enable_filter)

        # Date pickers row
        date_pickers_layout = QHBoxLayout()

        # Start date
        start_label = QLabel("From:")
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDisplayFormat("yyyy-MM-dd")
        self.date_start.setEnabled(False)
        self.date_start.setDate(QDate.currentDate().addMonths(-1))

        # End date
        end_label = QLabel("To:")
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDisplayFormat("yyyy-MM-dd")
        self.date_end.setEnabled(False)
        self.date_end.setDate(QDate.currentDate())

        date_pickers_layout.addWidget(start_label)
        date_pickers_layout.addWidget(self.date_start)
        date_pickers_layout.addSpacing(20)
        date_pickers_layout.addWidget(end_label)
        date_pickers_layout.addWidget(self.date_end)
        date_pickers_layout.addStretch()

        date_filter_layout.addLayout(date_pickers_layout)

        # Info label
        self.lbl_date_info = QLabel(
            "ℹ️ Filter rows by action_date. Format: YYYY-MM-DD"
        )
        self.lbl_date_info.setStyleSheet("color: gray; font-size: 10px;")
        date_filter_layout.addWidget(self.lbl_date_info)

        date_filter_group.setLayout(date_filter_layout)
        main_layout.addWidget(date_filter_group)

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

        main_layout.addWidget(self.table)

        # Buttons row
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

        # ========== COLLAPSIBLE CONSOLE SECTION ==========
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

    def _toggle_console(self):
        """Toggle console visibility."""
        if self.log_text.isVisible():
            self.log_text.hide()
            self.btn_toggle_console.setText("▶ Expand")
        else:
            self.log_text.show()
            self.btn_toggle_console.setText("▼ Collapse")

    # ---------------------- Date Filter Toggle ----------------------

    def _toggle_date_filter(self, state):
        """Enable/disable date filter controls."""
        enabled = state == Qt.CheckState.Checked.value
        self.date_start.setEnabled(enabled)
        self.date_end.setEnabled(enabled)
        self.date_filter_enabled = enabled

    # ---------------------- Drive Loading ----------------------

    def _append_log(self, text: str):
        """Append text to log window and scroll to bottom."""
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
        self.log_text.insertPlainText(text)
        self.log_text.moveCursor(QTextCursor.MoveOperation.End)

    def _load_drive_files(self):
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

            files_raw = get_all_excel_files_from_folder(
                drive_service, self.folder_id
            )
            self.drive_files = [
                DriveFileInfo(
                    file_id=f["id"],
                    name=f["name"],
                    mime_type=f.get("mimeType", ""),
                )
                for f in files_raw
            ]

            if not self.drive_files:
                self._append_log("⚠️ No Excel files found in the folder.\n")
                QMessageBox.information(
                    self,
                    "No Files",
                    "No Excel files were found in the configured Google Drive folder.",
                )
            else:
                self._append_log(
                    f"✓ Found {len(self.drive_files)} Excel file(s).\n\n"
                )

            self._populate_table()

        except Exception as e:
            self._append_log(f"❌ ERROR while loading Drive files: {e}\n")
            QMessageBox.critical(
                self,
                "Drive Error",
                f"An error occurred while accessing Google Drive:\n{e}",
            )
            self.btn_run.setEnabled(False)

    def _populate_table(self):
        self.table.setRowCount(len(self.drive_files))

        for row, file_info in enumerate(self.drive_files):
            # Checkbox cell
            item_check = QTableWidgetItem()
            item_check.setFlags(
                Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable
            )
            item_check.setCheckState(Qt.CheckState.Unchecked)

            # Name cell
            item_name = QTableWidgetItem(file_info.name)
            item_name.setFlags(Qt.ItemFlag.ItemIsEnabled)

            self.table.setItem(row, 0, item_check)
            self.table.setItem(row, 1, item_name)

    # ---------------------- Selection Helpers ----------------------

    def _select_all(self):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item is not None:
                item.setCheckState(Qt.CheckState.Checked)

    def _deselect_all(self):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item is not None:
                item.setCheckState(Qt.CheckState.Unchecked)

    def _get_selected_files(self) -> List[DriveFileInfo]:
        selected: List[DriveFileInfo] = []
        for row in range(self.table.rowCount()):
            check_item = self.table.item(row, 0)
            if check_item is None:
                continue
            if check_item.checkState() == Qt.CheckState.Checked:
                selected.append(self.drive_files[row])
        return selected

    # ---------------------- Open Output Folder ----------------------

    def _open_output_folder(self):
        """Open the DATA folder (root output directory) in file explorer."""
        from doc_validator.config import DATA_FOLDER

        if not os.path.exists(DATA_FOLDER):
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
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Opening Folder",
                f"Could not open folder:\n{e}",
            )

    # ---------------------- Run Button / Worker ----------------------

    def _on_run_clicked(self):
        if not self.api_key or not self.folder_id:
            QMessageBox.critical(
                self,
                "Credentials Error",
                "Cannot run: API key or folder ID is not set.",
            )
            return

        selected_files = self._get_selected_files()
        if not selected_files:
            QMessageBox.information(
                self,
                "No Files Selected",
                "Please select at least one file to process.",
            )
            return

        # Disable Run button while processing
        self.btn_run.setEnabled(False)
        self.btn_refresh.setEnabled(False)

        # Get date filter settings
        filter_start = None
        filter_end = None

        if self.date_filter_enabled:
            filter_start = self.date_start.date().toPyDate()
            filter_end = self.date_end.date().toPyDate()

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

        # Create progress dialog
        self.progress_dialog = QProgressDialog(
            "Initializing...",
            "Cancel",
            0,
            100,
            self,
        )
        self.progress_dialog.setWindowTitle("Processing Files")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setValue(0)

        # Start background worker
        self.worker = ProcessingWorker(
            api_key=self.api_key,
            folder_id=self.folder_id,
            selected_files=selected_files,
            filter_start_date=filter_start,
            filter_end_date=filter_end,
        )
        self.worker.log_message.connect(self._append_log)
        self.worker.progress_updated.connect(self._update_progress)
        self.worker.finished_with_results.connect(self._on_processing_finished)

        # Connect cancel button
        self.progress_dialog.canceled.connect(self.worker.cancel)

        self.worker.start()

    def _update_progress(self, percentage: int, status_text: str):
        """Update progress dialog with percentage and status."""
        if self.progress_dialog:
            self.progress_dialog.setValue(percentage)
            self.progress_dialog.setLabelText(
                f"Progress: {percentage}%\n\n{status_text}"
            )

    def _on_processing_finished(self, results: List[Dict[str, Any]]):
        self._append_log("\n✓ Processing thread has finished.\n")

        # Close progress dialog
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None

        # Re-enable buttons
        self.btn_run.setEnabled(True)
        self.btn_refresh.setEnabled(True)

        # Count successes and failures
        success_count = sum(1 for r in results if r.get("output_file"))
        total = len(results)
        failed_count = total - success_count

        # Summary message
        from doc_validator.config import DATA_FOLDER

        if success_count == total:
            msg = f"✓ All {total} file(s) processed successfully!"
        elif success_count > 0:
            msg = f"⚠️ Processed {success_count}/{total} file(s) successfully.\n{failed_count} file(s) failed."
        else:
            msg = f"❌ All {total} file(s) failed to process."

        msg += f"\n\nOutput directory:\n{DATA_FOLDER}"

        QMessageBox.information(
            self,
            "Processing Complete",
            msg,
        )


# ---------------------------------------------------------------------
# Entry point for running the GUI
# ---------------------------------------------------------------------

def launch():
    """Launch the PyQt6 GUI."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    launch()