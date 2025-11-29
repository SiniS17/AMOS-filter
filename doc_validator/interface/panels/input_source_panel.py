from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QGroupBox,
    QSizePolicy,
)


class InputSourcePanel(QGroupBox):
    """
    Left-side input source panel (source selector + actions).
    MainWindow will connect signals and read public attributes directly.
    """

    def __init__(self, parent: Optional[QWidget] = None, default_path: str = "") -> None:
        super().__init__("📂 Input Source", parent)

        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #444;
                border-radius: 8px;
                margin-top: 12px;
                padding: 15px;
                background: #2a2a2a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2196F3;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        self.setLayout(main_layout)

        # ---- Source type row ----
        source_row = QHBoxLayout()
        source_row.addWidget(QLabel("Load files from:"))

        self.combo_source = QComboBox(self)
        self.combo_source.addItem("📁 Local Folder (INPUT)", "local")
        self.combo_source.addItem("☁️  Google Drive", "drive")
        self.combo_source.setStyleSheet("""
            QComboBox {
                padding: 5px 10px;
                border: 2px solid #444;
                border-radius: 5px;
                background: #333;
                min-width: 0px;   /* let fixed width control the size */
            }
            QComboBox:hover {
                border-color: #2196F3;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
        """)
        # make the combo just wide enough for its content + a bit
        self.combo_source.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToContents
        )
        hint_width = self.combo_source.sizeHint().width()
        self.combo_source.setFixedWidth(hint_width + 30)

        source_row.addWidget(self.combo_source)
        source_row.addStretch()
        main_layout.addLayout(source_row)

        # ---- Hidden folder path (kept for logic, not shown) ----
        self.label_folder_path = QLabel(default_path or "—")
        self.label_folder_path.hide()

        # ---- Buttons row: Browse + Open Output ----
        buttons_row = QHBoxLayout()

        self.btn_browse_folder = QPushButton("📁 Browse...")
        buttons_row.addWidget(self.btn_browse_folder)

        self.btn_open_output = QPushButton("📂 Open Output")
        buttons_row.addWidget(self.btn_open_output)

        buttons_row.addStretch()
        main_layout.addLayout(buttons_row)

        # ---- Drive info ----
        self.label_drive_info = QLabel("☁️  Using configured Google Drive folder")
        self.label_drive_info.setStyleSheet("color: #4CAF50; font-style: italic;")
        self.label_drive_info.hide()  # start hidden (local mode)
        main_layout.addWidget(self.label_drive_info)

        # main_layout.addStretch()
