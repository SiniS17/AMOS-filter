# doc_validator/interface/panels/date_filter_panel.py (UPDATED)

from __future__ import annotations

from datetime import date
from typing import Optional, Tuple

from PyQt6.QtCore import QDate, pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QSizePolicy,
    QWidget,
)

from doc_validator.interface.widgets.smart_date_edit import SmartDateLineEdit


class DateFilterPanel(QWidget):
    """
    Reusable 'Date Filter (Optional)' component.
    Supports both vertical (sidebar) and horizontal (inline) layouts.

    Features:
      - Checkbox: Enable date filtering
      - Two SmartDateLineEdit fields: From / To
      - Public API:
          * is_enabled() -> bool
          * get_range() -> tuple[date | None, date | None]
    """

    filter_toggled = pyqtSignal(bool)

    def __init__(self, parent=None, compact_mode: bool = False):
        """
        Args:
            parent: Parent widget
            compact_mode: If True, use horizontal layout for inline display
        """
        super().__init__(parent)
        self.compact_mode = compact_mode
        self._build_ui()

    # ------------------------------------------------------------------ #
    # UI
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        if self.compact_mode:
            self._build_compact_ui()
        else:
            self._build_full_ui()

    def _build_compact_ui(self) -> None:
        """Compact horizontal layout for inline display."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Checkbox
        self.chk_enable = QCheckBox("📅 Date Filter:")
        self.chk_enable.setChecked(False)
        self.chk_enable.setStyleSheet("font-weight: bold; color: #2196F3;")
        layout.addWidget(self.chk_enable)

        # From
        layout.addWidget(QLabel("From:"))
        start_initial = QDate.currentDate().addMonths(-1)
        self.date_start = SmartDateLineEdit(start_initial)
        self.date_start.setEnabled(False)
        self.date_start.setFixedWidth(120)
        layout.addWidget(self.date_start)

        # To
        layout.addWidget(QLabel("To:"))
        end_initial = QDate.currentDate()
        self.date_end = SmartDateLineEdit(end_initial)
        self.date_end.setEnabled(False)
        self.date_end.setFixedWidth(120)
        layout.addWidget(self.date_end)

        # Connections
        self.chk_enable.stateChanged.connect(self._on_toggle)

    def _build_full_ui(self) -> None:
        """Full vertical layout for sidebar display."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        # Title
        title = QLabel("📅 Date Filter (Optional)")
        title.setStyleSheet("color: #2196F3; font-weight: bold;")
        layout.addWidget(title)

        # Checkbox
        self.chk_enable = QCheckBox("Enable date filtering")
        self.chk_enable.setChecked(False)
        self.chk_enable.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        )
        layout.addWidget(self.chk_enable)

        # From / To
        dates_row = QHBoxLayout()

        start_label = QLabel("From:")
        start_initial = QDate.currentDate().addMonths(-1)
        self.date_start = SmartDateLineEdit(start_initial)
        self.date_start.setEnabled(False)

        end_label = QLabel("To:")
        end_initial = QDate.currentDate()
        self.date_end = SmartDateLineEdit(end_initial)
        self.date_end.setEnabled(False)

        dates_row.addWidget(start_label)
        dates_row.addWidget(self.date_start)
        dates_row.addSpacing(20)
        dates_row.addWidget(end_label)
        dates_row.addWidget(self.date_end)
        dates_row.addStretch()

        layout.addLayout(dates_row)

        # Hint
        hint = QLabel("Format: YYYY-MM-DD or +/-Nd/M/Y")
        hint.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(hint)

        # Connections
        self.chk_enable.stateChanged.connect(self._on_toggle)

    # ------------------------------------------------------------------ #
    # Behaviour
    # ------------------------------------------------------------------ #

    def _on_toggle(self, state: int) -> None:
        enabled = bool(state)
        self.date_start.setEnabled(enabled)
        self.date_end.setEnabled(enabled)
        self.filter_toggled.emit(enabled)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def is_enabled(self) -> bool:
        """Return True if date filtering is turned on."""
        return self.chk_enable.isChecked()

    def get_range(self) -> Tuple[Optional[date], Optional[date]]:
        """
        Return (start, end) dates if enabled.

        Uses SmartDateLineEdit.resolve_date() so it understands
        YYYY-MM-DD and +/-Nd/M/Y.

        Raises:
            ValueError if input text is invalid when filter is enabled.
        """
        if not self.is_enabled():
            return None, None

        start = end = None

        text_start = self.date_start.text().strip()
        text_end = self.date_end.text().strip()

        if text_start:
            start = self.date_start.resolve_date()
        if text_end:
            end = self.date_end.resolve_date()

        return start, end