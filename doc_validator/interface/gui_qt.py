# doc_validator/interface/gui_qt.py

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
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
    download_file_from_drive,
    read_credentials_file,
)
from doc_validator.core.excel_pipeline import process_excel


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
    finished_with_results = pyqtSignal(list)

    def __init__(
        self,
        api_key: str,
        folder_id: str,
        selected_files: List[DriveFileInfo],
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.api_key = api_key
        self.folder_id = folder_id
        self.selected_files = selected_files

    def run(self):
        """
        Run in background thread:
        - authenticate
        - download each selected file
        - process it with process_excel
        - emit log messages and final results
        """
        results: List[Dict[str, Any]] = []

        # Redirect stdout so all prints from process_excel()
        # also appear in the GUI log window.
        original_stdout = sys.stdout
        stream = EmittingStream(LogEmitter(), original_stdout)

        # Connect inner emitter to our signal
        stream.emitter.message.connect(self.log_message.emit)

        sys.stdout = stream

        try:
            self.log_message.emit("Authenticating with Google Drive API...\n")
            drive_service = authenticate_drive_api(self.api_key)
            self.log_message.emit("✓ Authentication successful.\n\n")

            total = len(self.selected_files)
            self.log_message.emit(
                f"Processing {total} selected file(s) from Drive folder...\n"
            )

            for idx, file_info in enumerate(self.selected_files, start=1):
                self.log_message.emit(
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
                    self.log_message.emit(
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

                self.log_message.emit(
                    f"Local file path: {local_path}\n"
                )

                # Run the Excel processing pipeline
                output_file = process_excel(local_path)

                if output_file:
                    self.log_message.emit(
                        f"✓ Processing finished for {file_info.name}\n"
                        f"  Output: {output_file}\n"
                    )
                else:
                    self.log_message.emit(
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

            self.log_message.emit("\nAll selected files have been processed.\n")

        except Exception as e:
            # In case of unexpected error
            import traceback

            self.log_message.emit(f"\n✗ ERROR: {str(e)}\n")
            self.log_message.emit(traceback.format_exc())

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

        self.setWindowTitle("Doc Validator - PyQt6 GUI")
        self.resize(900, 600)

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

    def _setup_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)

        main_layout = QVBoxLayout()
        central.setLayout(main_layout)

        # Top label
        label = QLabel("Excel files in configured Google Drive folder:")
        label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(label)

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

        self.btn_run = QPushButton("Run")
        self.btn_run.clicked.connect(self._on_run_clicked)

        btn_layout.addWidget(self.btn_select_all)
        btn_layout.addWidget(self.btn_deselect_all)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_run)

        main_layout.addLayout(btn_layout)

        # Log label
        log_label = QLabel("Console output:")
        log_label.setStyleSheet("font-weight: bold; margin-top: 8px;")
        main_layout.addWidget(log_label)

        # Console-style log output
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.log_text.setStyleSheet(
            "font-family: Consolas, 'Courier New', monospace; font-size: 11px;"
        )
        main_layout.addWidget(self.log_text)

    # ---------------------- Drive Loading ----------------------

    def _append_log(self, text: str):
        """
        Append text to log window and scroll to bottom.
        """
        self.log_text.moveCursor(self.log_text.textCursor().End)
        self.log_text.insertPlainText(text)
        self.log_text.moveCursor(self.log_text.textCursor().End)

    def _load_drive_files(self):
        """
        Read credentials and list all Excel files in the configured folder.
        User is not allowed to change the folder.
        """
        self._append_log(
            f"Reading credentials from: {LINK_FILE}\n"
        )
        api_key, folder_id = read_credentials_file(LINK_FILE)

        if not api_key or not folder_id:
            self._append_log(
                "ERROR: Invalid credentials (GG_API_KEY or GG_FOLDER_ID missing).\n"
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
            self._append_log("Authenticating with Google Drive API...\n")
            drive_service = authenticate_drive_api(self.api_key)
            self._append_log("✓ Authentication successful.\n")
            self._append_log(
                "Fetching Excel file list from configured folder...\n"
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
                self._append_log(
                    "No Excel files found in the folder.\n"
                )
                QMessageBox.information(
                    self,
                    "No Files",
                    "No Excel files were found in the configured Google Drive folder.",
                )
            else:
                self._append_log(
                    f"Found {len(self.drive_files)} Excel file(s).\n"
                )

            self._populate_table()

        except Exception as e:
            self._append_log(f"ERROR while loading Drive files: {e}\n")
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
        self._append_log(
            "\n" + "=" * 60 + "\n"
            "Starting processing of selected files...\n"
            + "=" * 60 + "\n"
        )

        # Start background worker
        self.worker = ProcessingWorker(
            api_key=self.api_key,
            folder_id=self.folder_id,
            selected_files=selected_files,
        )
        self.worker.log_message.connect(self._append_log)
        self.worker.finished_with_results.connect(self._on_processing_finished)
        self.worker.start()

    def _on_processing_finished(self, results: List[Dict[str, Any]]):
        self._append_log("\nProcessing thread has finished.\n")
        self.btn_run.setEnabled(True)

        # Determine output directory (from first successful output)
        output_dir = None
        for r in results:
            out = r.get("output_file")
            if out:
                output_dir = os.path.dirname(out)
                break

        if output_dir:
            msg = f"Data has been filtered.\n\nOutput directory:\n{output_dir}"
        else:
            msg = "Data has been filtered.\n\nNo successful output files were created."

        QMessageBox.information(
            self,
            "Processing Complete",
            msg,
        )


# ---------------------------------------------------------------------
# Entry point for running the GUI
# ---------------------------------------------------------------------

def launch():
    """
    Launch the PyQt6 GUI.
    Usage:
        python -m doc_validator.interface.gui_qt
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    launch()
