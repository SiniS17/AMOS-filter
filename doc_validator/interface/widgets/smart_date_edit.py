import re
import calendar
from datetime import date, datetime, timedelta

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import (
    QLineEdit,
    QDialog, QVBoxLayout, QDialogButtonBox, QCalendarWidget
)


class SmartDateLineEdit(QLineEdit):
    """
    Date field with:
      - single click: *ends* select-all and places caret
      - double click: open calendar popup
      - supports relative input: -1d, +2d, -1m, +1y, etc.
        relative to last valid date.
    """

    def __init__(self, initial_qdate: QDate | None = None, parent=None):
        super().__init__(parent)

        if initial_qdate is None:
            initial_qdate = QDate.currentDate()

        self._last_valid_date: date = initial_qdate.toPyDate()
        self.setText(initial_qdate.toString("yyyy-MM-dd"))
        self.setPlaceholderText("YYYY-MM-DD or +/-Nd/M/Y")

        # ENTER: resolve relative date immediately
        self.returnPressed.connect(self._on_return_pressed)

        # Start life in "select all" state
        self.selectAll()

    # ---------------------------------------------------------
    # Focus & mouse behaviour
    # ---------------------------------------------------------

    def focusInEvent(self, event):
        """
        When the widget gains focus:
          - If it was via keyboard / programmatically → select all
          - If it was via mouse click → do NOT select all
            (so first click just removes the selection & positions caret)
        """
        super().focusInEvent(event)

        reason = getattr(event, "reason", lambda: Qt.FocusReason.OtherFocusReason)()
        if reason != Qt.FocusReason.MouseFocusReason:
            # e.g. Tab focus or we call setFocus() from code
            self.selectAll()

    def mouseDoubleClickEvent(self, event):
        # 2 clicks -> open calendar popup
        self._open_calendar_popup()
        event.accept()

    # ---------------------------------------------------------
    # Calendar popup
    # ---------------------------------------------------------

    def _open_calendar_popup(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Select date")
        layout = QVBoxLayout(dlg)

        cal = QCalendarWidget(dlg)
        d = self._last_valid_date
        cal.setSelectedDate(QDate(d.year, d.month, d.day))
        layout.addWidget(cal)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel,
            parent=dlg,
        )
        layout.addWidget(buttons)

        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)

        if dlg.exec():
            qd = cal.selectedDate()
            self._update_from_date(qd.toPyDate())
            # After choosing from calendar → select all again
            self.selectAll()

    # ---------------------------------------------------------
    # Date parsing
    # ---------------------------------------------------------

    def _update_from_date(self, new_date: date):
        self._last_valid_date = new_date
        self.setText(new_date.strftime("%Y-%m-%d"))

    def resolve_date(self) -> date:
        """
        Parse current text.

        Supports:
            - YYYY-MM-DD (absolute)
            - +Nd / -Nd  (days)
            - +Nm / -Nm  (months)
            - +Ny / -Ny  (years)
        """
        text = self.text().strip()
        if not text:
            raise ValueError("Empty date")

        # Relative pattern
        m = re.fullmatch(r"([+-])(\d+)([dmyDMy])", text)
        base = self._last_valid_date

        if m:
            sign, num_str, unit = m.groups()
            n = int(num_str)
            if sign == "-":
                n = -n
            unit = unit.lower()

            if unit == "d":
                result = base + timedelta(days=n)

            elif unit == "m":
                month = base.month + n
                year = base.year
                while month > 12:
                    month -= 12
                    year += 1
                while month < 1:
                    month += 12
                    year -= 1
                last_day = calendar.monthrange(year, month)[1]
                day = min(base.day, last_day)
                result = date(year, month, day)

            else:  # 'y'
                year = base.year + n
                month = base.month
                last_day = calendar.monthrange(year, month)[1]
                day = min(base.day, last_day)
                result = date(year, month, day)

        else:
            # Absolute format
            result = datetime.strptime(text, "%Y-%m-%d").date()

        self._update_from_date(result)
        return result

    # ---------------------------------------------------------
    # ENTER key behaviour
    # ---------------------------------------------------------

    def _on_return_pressed(self):
        """
        When user hits Enter:
          - parse the date (absolute or relative)
          - update text
          - keep 'select all' active so they can immediately retype
        """
        try:
            self.resolve_date()
            self.selectAll()
        except ValueError:
            # Invalid / incomplete input → do nothing, let user keep editing
            pass
