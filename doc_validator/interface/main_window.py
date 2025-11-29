# doc_validator/interface/main_window.py
# PHASE 2 ENHANCED: File details, modern theme, enhanced styling

from __future__ import annotations

import os
import platform
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QTextCursor, QColor, QFont, QIcon, QPixmap
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
    QLineEdit,
    QFileDialog,
    QProgressBar,
    QSplitter, QCheckBox,  # ⬅️ NEW
)

from doc_validator.config import LINK_FILE
from doc_validator.core.drive_io import read_credentials_file
from doc_validator.core.input_source_manager import (
    FileInfo,
    get_local_excel_files,
    get_drive_excel_files,
    get_default_input_folder,
)
from doc_validator.interface.panels.date_filter_panel import DateFilterPanel
from doc_validator.interface.panels.input_source_panel import InputSourcePanel
from doc_validator.interface.styles.theme import get_dark_theme_stylesheet
from doc_validator.interface.workers.processing_worker import ProcessingWorker


class MainWindow(QMainWindow):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.setWindowTitle("AMOS Documentation Validator")
        self.resize(1200, 800)

        # Apply dark theme
        self.setStyleSheet(get_dark_theme_stylesheet())

        # Credentials / Drive folder info
        self.api_key: Optional[str] = None
        self.folder_id: Optional[str] = None

        # File source management
        self.all_files: List[FileInfo] = []
        self.filtered_files: List[FileInfo] = []
        self._status_row_map: dict[str, list[int]] = {}
        self.current_source_type: str = "local"
        self.current_local_path: str = get_default_input_folder()

        # Worker thread reference
        self.worker: Optional[ProcessingWorker] = None

        # Build UI
        self._setup_ui()

        # Load credentials
        self._load_credentials()

        # Load files from default source
        self._load_files_from_current_source()

    def _on_header_clicked(self, index: int) -> None:
        """Handle clicks on table header sections."""
        if index == 0:
            # Click on the first header cell = refresh
            self._load_files_from_current_source()

    # ---------------------- UI Setup ----------------------

    def _setup_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        central.setLayout(main_layout)

        # ========== HEADER WITH LOGO ==========
        header_layout = QHBoxLayout()

        # Compute path relative to main_window.py
        project_root = Path(__file__).resolve().parent.parent
        logo_path = project_root / "resources" / "icons" / "app_logo.png"

        logo_box = QHBoxLayout()
        logo_box.setSpacing(10)

        # --- Logo image ---
        logo_image = QLabel()
        pix = QPixmap(str(logo_path))

        # scale to nice height, keep sharp edges
        pix = pix.scaledToHeight(32, Qt.TransformationMode.SmoothTransformation)
        logo_image.setPixmap(pix)

        # --- App title ---
        logo_text = QLabel("AMOS Document Validators")
        logo_text.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2196F3;
        """)

        logo_box.addWidget(logo_image)
        logo_box.addWidget(logo_text)
        logo_box.addStretch()

        header_layout.addLayout(logo_box)

        header_layout.addStretch()

        version_label = QLabel("v2.5.22")
        version_label.setStyleSheet("color: #888; font-size: 11px;")
        header_layout.addWidget(version_label)

        main_layout.addLayout(header_layout)

        # ========== MAIN HORIZONTAL SPLITTER ==========
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        splitter.setHandleWidth(4)
        main_layout.addWidget(splitter, 1)  # stretch factor 1

        # ---------- LEFT COLUMN (Input Source + Date Filter) ----------
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(8)
        left_widget.setLayout(left_layout)

        # Input Source panel (new module)
        self.input_panel = InputSourcePanel(self, default_path=self.current_local_path)
        left_layout.addWidget(self.input_panel)

        self.input_panel.open_output_clicked.connect(self._open_output_folder)
        # expose inner widgets so existing methods keep working
        self.combo_source = self.input_panel.combo_source
        self.label_folder_path = self.input_panel.label_folder_path
        self.btn_browse_folder = self.input_panel.btn_browse_folder
        self.label_drive_info = self.input_panel.label_drive_info

        self.combo_source.currentIndexChanged.connect(self._on_source_changed)
        self.btn_browse_folder.clicked.connect(self._browse_local_folder)

        # Date filter panel under input source
        self.date_filter_panel = DateFilterPanel(self)
        left_layout.addWidget(self.date_filter_panel)
        # ---------- Action Step Control toggle ----------
        self.asc_checkbox = QCheckBox("Run Action Step Control (ASC)")
        self.asc_checkbox.setChecked(True)  # default ON
        self.asc_checkbox.setStyleSheet("color: #2196F3; font-weight: bold;")
        left_layout.addWidget(self.asc_checkbox)

        left_layout.addStretch()

        splitter.addWidget(left_widget)

        # ---------- RIGHT COLUMN (Toolbar + Files + Console) ----------
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.setSpacing(8)
        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)

        # initial sizes (approx.)
        splitter.setSizes([350, 850])

        # ========== SEARCH BAR + FILE SECTION ==========
        header_row = QHBoxLayout()

        file_section_label = QLabel("Input Files")
        file_section_label.setStyleSheet("""
            font-weight: bold;
            font-size: 14px;
            color: #2196F3;
            margin-top: 4px;
        """)
        header_row.addWidget(file_section_label)

        header_row.addStretch()

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 16px; padding-right: 4px;")
        header_row.addWidget(search_icon)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Type to filter files by name...")
        self.search_bar.textChanged.connect(self._on_search_changed)
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 6px 10px;
                border: 2px solid #444;
                border-radius: 5px;
                background: #2a2a2a;
                font-size: 13px;
                min-width: 220px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """)
        header_row.addWidget(self.search_bar)

        right_layout.addLayout(header_row)

        # ========== FILE LIST TABLE ==========
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "", "File Name", "Source", "Size", "Modified", "Status"
        ])

        # Column sizes
        header = self.table.horizontalHeader()

        # Refresh column (0) – fixed size, square-ish
        refresh_size = 32  # tweak 32–36 if you want bigger
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, refresh_size + 4)

        # Other columns
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # File Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Source
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Size
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Modified
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Status

        # Make header sections tight so the icon fills the cell
        header.setMinimumHeight(refresh_size + 4)

        # ---------- big refresh icon in first header cell ----------
        refresh_item = QTableWidgetItem()
        # path relative to this file: /resources/icons/refresh.png
        project_root = Path(__file__).resolve().parent.parent
        refresh_icon_path = project_root / "resources" / "icons" / "refresh.png"
        refresh_item.setIcon(QIcon(str(refresh_icon_path)))
        refresh_item.setText("")  # icon only
        refresh_item.setSizeHint(QSize(refresh_size, refresh_size))  # fills ~100% of cell
        self.table.setHorizontalHeaderItem(0, refresh_item)

        # Click on header[0] = refresh
        header.sectionClicked.connect(self._on_header_clicked)

        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #3a3a3a;
                background-color: #2a2a2a;
                alternate-background-color: #252525;
                border: 2px solid #444;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 6px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #1976D2;
            }
            QHeaderView::section {
                background-color: #333;
                color: #2196F3;
                padding: 8px;
                border: none;
                border-right: 1px solid #444;
                font-weight: bold;
            }
            QTableWidget::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
            }
            QTableWidget::indicator:unchecked {
                background-color: #333;
                border: 2px solid #666;
            }
            QTableWidget::indicator:unchecked:hover {
                background-color: #3a3a3a;
                border-color: #2196F3;
            }
            QTableWidget::indicator:checked {
                background-color: #2196F3;
                border: 2px solid #2196F3;
                image: url(none);
            }
            QTableWidget::indicator:checked:hover {
                background-color: #42A5F5;
            }
        """)

        right_layout.addWidget(self.table, 1)  # stretch to fill

        # ========== TABLE CONTROL BUTTONS ==========
        btn_layout = QHBoxLayout()

        self.btn_select_all = QPushButton("✓ Select All")
        self.btn_select_all.clicked.connect(self._select_all)

        self.btn_deselect_all = QPushButton("✗ Deselect All")
        self.btn_deselect_all.clicked.connect(self._deselect_all)

        btn_layout.addWidget(self.btn_select_all)
        btn_layout.addWidget(self.btn_deselect_all)
        btn_layout.addStretch()

        self.btn_run = QPushButton("▶ Run Processing")
        self.btn_run.clicked.connect(self._on_run_clicked)
        self.btn_run.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 14px;
                padding: 10px 30px;
                background: #4CAF50;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                color: white;
            }
            QPushButton:hover {
                background: #66BB6A;
                border-color: #66BB6A;
            }
            QPushButton:pressed {
                background: #388E3C;
            }
            QPushButton:disabled {
                background: #555;
                border-color: #555;
                color: #888;
            }
        """)
        btn_layout.addWidget(self.btn_run)

        right_layout.addLayout(btn_layout)

        # ========== PROGRESS SECTION ==========
        self.progress_container = QWidget()
        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(0, 4, 0, 4)
        self.progress_container.setLayout(progress_layout)

        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("""
            font-weight: bold;
            color: #2196F3;
            font-size: 13px;
        """)
        progress_layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #444;
                border-radius: 8px;
                text-align: center;
                height: 24px;
                background: #2a2a2a;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3,
                    stop:1 #42A5F5
                );
                border-radius: 6px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)

        self.progress_container.hide()
        right_layout.addWidget(self.progress_container)

        # ========== CONSOLE OUTPUT ==========
        console_header = QHBoxLayout()
        console_label = QLabel("📝 Console Output")
        console_label.setStyleSheet("""
            font-weight: bold;
            font-size: 13px;
            color: #2196F3;
            margin-top: 4px;
        """)

        self.btn_toggle_console = QPushButton("▼ Collapse")
        self.btn_toggle_console.setMaximumWidth(100)
        self.btn_toggle_console.clicked.connect(self._toggle_console)
        self.btn_toggle_console.setStyleSheet("""
            QPushButton {
                padding: 4px 8px;
                border: 1px solid #444;
                border-radius: 3px;
                background: #333;
            }
            QPushButton:hover {
                background: #444;
            }
        """)

        console_header.addWidget(console_label)
        console_header.addStretch()
        console_header.addWidget(self.btn_toggle_console)

        right_layout.addLayout(console_header)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.log_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                background: #1a1a1a;
                border: 2px solid #444;
                border-radius: 5px;
                padding: 8px;
                color: #00FF00;
            }
        """)
        self.log_text.setMaximumHeight(200)
        right_layout.addWidget(self.log_text)

    # ---------------------- Console Toggle ----------------------

    def _toggle_console(self) -> None:
        if self.log_text.isVisible():
            self.log_text.hide()
            self.btn_toggle_console.setText("▲ Expand")
        else:
            self.log_text.show()
            self.btn_toggle_console.setText("▼ Collapse")

    # ---------------------- Helpers ----------------------

    def _append_log(self, text: str) -> None:
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
        self.log_text.insertPlainText(text)
        self.log_text.moveCursor(QTextCursor.MoveOperation.End)

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    # ---------------------- Credentials ----------------------

    def _load_credentials(self) -> None:
        api_key, folder_id = read_credentials_file(LINK_FILE)
        if api_key and folder_id:
            self.api_key = api_key
            self.folder_id = folder_id
            self._append_log(f"✓ Drive credentials loaded\n")
        else:
            self._append_log("⚠️  Drive credentials not found\n")

    # ---------------------- Source Management ----------------------

    def _on_source_changed(self, index: int) -> None:
        source_type = self.combo_source.currentData()
        self.current_source_type = source_type

        if source_type == "local":
            self.label_folder_path.show()
            self.btn_browse_folder.show()
            self.label_drive_info.hide()
        else:
            self.label_folder_path.hide()
            self.btn_browse_folder.hide()
            self.label_drive_info.show()

        self._load_files_from_current_source()

    def _browse_local_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Input Folder",
            self.current_local_path,
            QFileDialog.Option.ShowDirsOnly
        )

        if folder:
            self.current_local_path = folder
            self.label_folder_path.setText(folder)
            self._load_files_from_current_source()

    def _load_files_from_current_source(self) -> None:
        self.log_text.clear()
        self.search_bar.clear()

        if self.current_source_type == "local":
            self._load_local_files()
        else:
            self._load_drive_files()

    def _load_local_files(self) -> None:
        self._append_log(f"📂 Loading: {self.current_local_path}\n")
        self.all_files = get_local_excel_files(self.current_local_path)

        if not self.all_files:
            self._append_log("⚠️  No Excel files found\n")
        else:
            self._append_log(f"✓ Found {len(self.all_files)} file(s)\n")

        self.filtered_files = self.all_files.copy()
        self._populate_table()

    def _load_drive_files(self) -> None:
        if not self.api_key or not self.folder_id:
            self._append_log("❌ Drive credentials not configured\n")
            QMessageBox.critical(self, "Error", "Drive credentials missing")
            return

        try:
            self._append_log("🔐 Authenticating...\n")
            self.all_files = get_drive_excel_files(self.api_key, self.folder_id)

            if not self.all_files:
                self._append_log("⚠️  No files found\n")
            else:
                self._append_log(f"✓ Found {len(self.all_files)} file(s)\n")

            self.filtered_files = self.all_files.copy()
            self._populate_table()

        except Exception as e:
            self._append_log(f"❌ Error: {e}\n")
            QMessageBox.critical(self, "Error", str(e))

    # ---------------------- Search ----------------------

    def _on_search_changed(self, text: str) -> None:
        search_text = text.strip().lower()

        if not search_text:
            self.filtered_files = self.all_files.copy()
        else:
            self.filtered_files = [
                f for f in self.all_files
                if search_text in f.name.lower()
            ]

        self._populate_table()

    # ---------------------- Table Population ----------------------

    def _populate_table(self) -> None:
        self.table.setRowCount(0)

        for row_idx, file_info in enumerate(self.filtered_files):
            self.table.insertRow(row_idx)

            # Checkbox
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk_item.setCheckState(Qt.CheckState.Unchecked)
            chk_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, chk_item)

            # File name
            name_item = QTableWidgetItem(file_info.name)
            name_item.setFont(QFont("Segoe UI", 10))
            self.table.setItem(row_idx, 1, name_item)

            # Source
            source_text = "📁 Local" if file_info.source_type == "local" else "☁️  Drive"
            source_item = QTableWidgetItem(source_text)
            source_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 2, source_item)

            # File size
            if file_info.local_path and os.path.exists(file_info.local_path):
                size = os.path.getsize(file_info.local_path)
                size_text = self._format_file_size(size)
            else:
                size_text = "—"
            size_item = QTableWidgetItem(size_text)
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 3, size_item)

            # Modified date
            if file_info.local_path and os.path.exists(file_info.local_path):
                mtime = os.path.getmtime(file_info.local_path)
                date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            else:
                date_str = "—"
            date_item = QTableWidgetItem(date_str)
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            date_item.setForeground(QColor("#888"))
            self.table.setItem(row_idx, 4, date_item)

            # Status (empty initially)
            status_item = QTableWidgetItem("")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 5, status_item)

        self.table.resizeRowsToContents()

    # ---------------------- Selection ----------------------

    def _select_all(self) -> None:
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                item.setCheckState(Qt.CheckState.Checked)

    def _deselect_all(self) -> None:
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                item.setCheckState(Qt.CheckState.Unchecked)

    # ---------------------- Open Output ----------------------

    def _open_output_folder(self) -> None:
        from doc_validator.config import DATA_FOLDER

        if not os.path.isdir(DATA_FOLDER):
            QMessageBox.warning(self, "Error", f"Folder not found:\n{DATA_FOLDER}")
            return

        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(DATA_FOLDER)
            elif system == "Darwin":
                subprocess.Popen(["open", DATA_FOLDER])
            else:
                subprocess.Popen(["xdg-open", DATA_FOLDER])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open folder:\n{e}")

    # ---------------------- Run Processing ----------------------

    def _on_run_clicked(self) -> None:
        # Map file name -> list of row indices that were selected
        self._status_row_map = {}

        selected_files: List[FileInfo] = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                file_info = self.filtered_files[row]
                selected_files.append(self.filtered_files[row])
                self._status_row_map.setdefault(file_info.name, []).append(row)

        if not selected_files:
            QMessageBox.warning(self, "No Selection", "Please select at least one file")
            return

        # Clear status for the rows that are about to be processed
        for rows in self._status_row_map.values():
            for row in rows:
                status_item = self.table.item(row, 5)
                if status_item:
                    status_item.setText("")
                    # optional: neutral color
                    # status_item.setForeground(QColor("#CCCCCC"))

        self.btn_run.setEnabled(False)

        filter_start: Optional[date] = None
        filter_end: Optional[date] = None

        if self.date_filter_panel.is_enabled():
            try:
                filter_start, filter_end = self.date_filter_panel.get_range()
            except ValueError:
                QMessageBox.warning(self, "Invalid Date", "Please check date format")
                self.btn_run.setEnabled(True)
                return

            self._append_log(f"\n📅 Filter: {filter_start} to {filter_end}\n")

        self._append_log("\n" + "=" * 60 + "\n▶ Starting...\n" + "=" * 60 + "\n")

        self.progress_container.show()
        self.progress_bar.setValue(0)
        self.progress_label.setText("Starting...")

        enable_asc = self.asc_checkbox.isChecked()

        self.worker = ProcessingWorker(
            api_key=self.api_key,
            folder_id=self.folder_id,
            selected_files=selected_files,
            filter_start_date=filter_start,
            filter_end_date=filter_end,
            enable_action_step_control=enable_asc,
        )

        self.worker.log_message.connect(self._append_log)
        self.worker.progress_updated.connect(self._update_progress)
        self.worker.finished_with_results.connect(self._on_processing_finished)
        self.worker.finished.connect(self._on_worker_thread_finished)

        self.worker.start()

    def _on_worker_thread_finished(self) -> None:
        if self.worker:
            self.worker.deleteLater()
            self.worker = None

    def _update_progress(self, value: int, status: str) -> None:
        self.progress_bar.setValue(value)
        self.progress_label.setText(status)

    def _on_processing_finished(self, results: list) -> None:
        self.progress_container.hide()
        self.btn_run.setEnabled(True)

        # Update status column ONLY for the rows that were actually selected
        for result in results:
            name = result.get("source_name")
            if not name:
                continue

            rows = self._status_row_map.get(name, [])
            for row in rows:
                status_item = self.table.item(row, 5)
                if not status_item:
                    continue

                if result.get("output_file"):
                    status_item.setText("✓ Success")
                    status_item.setForeground(QColor("#4CAF50"))
                else:
                    status_item.setText("✗ Failed")
                    status_item.setForeground(QColor("#F44336"))

        # Summary, same as before
        success_count = sum(1 for r in results if r.get("output_file"))
        total = len(results)
        failed_count = total - success_count

        from doc_validator.config import DATA_FOLDER

        if success_count == total:
            msg = f"✓ All {total} file(s) processed!"
        elif success_count > 0:
            msg = f"⚠️ Processed {success_count}/{total} file(s)\n{failed_count} failed"
        else:
            msg = f"❌ All {total} file(s) failed"

        msg += f"\n\nOutput: {DATA_FOLDER}"

        QMessageBox.information(self, "Complete", msg)


def launch() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
