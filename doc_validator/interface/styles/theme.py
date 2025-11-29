# doc_validator/interface/styles/theme.py
"""
Dark theme stylesheet for AMOSFilter GUI.
Provides modern, professional appearance with consistent styling.
"""


def get_dark_theme_stylesheet() -> str:
    """
    Return complete dark theme stylesheet for the application.

    Features:
    - Dark color scheme (#1a1a1a base, #2196F3 accent)
    - Rounded corners and subtle shadows
    - Smooth hover effects
    - Professional spacing and padding
    - Consistent border styling
    """
    return """
        /* ========================================
           GLOBAL APPLICATION STYLES
           ======================================== */

        QMainWindow {
            background-color: #1a1a1a;
            color: #e0e0e0;
        }

        QWidget {
            background-color: #1a1a1a;
            color: #e0e0e0;
            font-family: "Segoe UI", Arial, sans-serif;
            font-size: 12px;
        }

        /* ========================================
           LABELS
           ======================================== */

        QLabel {
            background: transparent;
            color: #e0e0e0;
            padding: 2px;
        }

        /* ========================================
           BUTTONS
           ======================================== */

        QPushButton {
            background-color: #2a2a2a;
            color: #e0e0e0;
            border: 2px solid #444;
            border-radius: 5px;
            padding: 6px 12px;
            font-weight: 500;
            min-height: 24px;
        }

        QPushButton:hover {
            background-color: #333;
            border-color: #2196F3;
        }

        QPushButton:pressed {
            background-color: #1a1a1a;
            border-color: #1976D2;
        }

        QPushButton:disabled {
            background-color: #222;
            color: #666;
            border-color: #333;
        }

        /* ========================================
           LINE EDITS & COMBO BOXES
           ======================================== */

        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #2a2a2a;
            color: #e0e0e0;
            border: 2px solid #444;
            border-radius: 5px;
            padding: 6px 8px;
            selection-background-color: #2196F3;
        }

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
            border-color: #2196F3;
        }

        QLineEdit:disabled, QTextEdit:disabled {
            background-color: #1a1a1a;
            color: #666;
            border-color: #333;
        }

        QComboBox {
            background-color: #2a2a2a;
            color: #e0e0e0;
            border: 2px solid #444;
            border-radius: 5px;
            padding: 6px 8px;
            min-width: 100px;
        }

        QComboBox:hover {
            border-color: #2196F3;
        }

        QComboBox::drop-down {
            border: none;
            width: 20px;
            padding-right: 10px;
        }

        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #e0e0e0;
            width: 0;
            height: 0;
        }

        QComboBox QAbstractItemView {
            background-color: #2a2a2a;
            color: #e0e0e0;
            border: 2px solid #444;
            border-radius: 5px;
            selection-background-color: #2196F3;
            selection-color: white;
            padding: 4px;
        }

        /* ========================================
           CHECKBOXES
           ======================================== */

        QCheckBox {
            spacing: 8px;
            color: #e0e0e0;
        }

        QCheckBox::indicator {
            width: 20px;
            height: 20px;
            border: 2px solid #666;
            border-radius: 4px;
            background-color: #2a2a2a;
        }

        QCheckBox::indicator:hover {
            border-color: #2196F3;
            background-color: #333;
        }

        QCheckBox::indicator:checked {
            background-color: #2196F3;
            border-color: #2196F3;
        }

        QCheckBox::indicator:checked:hover {
            background-color: #42A5F5;
        }

        QCheckBox::indicator:disabled {
            background-color: #1a1a1a;
            border-color: #444;
        }

        /* ========================================
           GROUP BOXES
           ======================================== */

        QGroupBox {
            border: 2px solid #444;
            border-radius: 8px;
            margin-top: 12px;
            padding: 15px 10px 10px 10px;
            background-color: #2a2a2a;
            font-weight: bold;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 5px;
            color: #2196F3;
            background-color: #2a2a2a;
        }

        /* ========================================
           SCROLL BARS
           ======================================== */

        QScrollBar:vertical {
            background-color: #2a2a2a;
            width: 12px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical {
            background-color: #555;
            border-radius: 6px;
            min-height: 30px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #2196F3;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }

        QScrollBar:horizontal {
            background-color: #2a2a2a;
            height: 12px;
            border-radius: 6px;
        }

        QScrollBar::handle:horizontal {
            background-color: #555;
            border-radius: 6px;
            min-width: 30px;
        }

        QScrollBar::handle:horizontal:hover {
            background-color: #2196F3;
        }

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }

        /* ========================================
           PROGRESS BARS
           ======================================== */

        QProgressBar {
            background-color: #2a2a2a;
            border: 2px solid #444;
            border-radius: 8px;
            text-align: center;
            color: white;
            font-weight: bold;
            height: 28px;
        }

        QProgressBar::chunk {
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 #2196F3,
                stop: 1 #42A5F5
            );
            border-radius: 6px;
        }

        /* ========================================
           MESSAGE BOXES
           ======================================== */

        QMessageBox {
            background-color: #2a2a2a;
            color: #e0e0e0;
        }

        QMessageBox QPushButton {
            min-width: 80px;
            padding: 8px 16px;
        }

        /* ========================================
           TOOL TIPS
           ======================================== */

        QToolTip {
            background-color: #333;
            color: #e0e0e0;
            border: 1px solid #2196F3;
            border-radius: 4px;
            padding: 4px;
        }

        /* ========================================
           DATE EDIT WIDGETS
           ======================================== */

        QDateEdit {
            background-color: #2a2a2a;
            color: #e0e0e0;
            border: 2px solid #444;
            border-radius: 5px;
            padding: 6px 8px;
        }

        QDateEdit:focus {
            border-color: #2196F3;
        }

        QDateEdit::drop-down {
            border: none;
            width: 20px;
        }

        QCalendarWidget {
            background-color: #2a2a2a;
            color: #e0e0e0;
        }

        QCalendarWidget QToolButton {
            color: #e0e0e0;
            background-color: #333;
            border: none;
            border-radius: 4px;
            padding: 4px;
        }

        QCalendarWidget QToolButton:hover {
            background-color: #2196F3;
        }

        QCalendarWidget QAbstractItemView {
            background-color: #2a2a2a;
            color: #e0e0e0;
            selection-background-color: #2196F3;
            selection-color: white;
        }

        /* ========================================
           MENU BAR & MENUS (if used)
           ======================================== */

        QMenuBar {
            background-color: #2a2a2a;
            color: #e0e0e0;
            border-bottom: 1px solid #444;
        }

        QMenuBar::item {
            background: transparent;
            padding: 4px 12px;
        }

        QMenuBar::item:selected {
            background-color: #2196F3;
        }

        QMenu {
            background-color: #2a2a2a;
            color: #e0e0e0;
            border: 2px solid #444;
            border-radius: 5px;
        }

        QMenu::item {
            padding: 6px 20px;
        }

        QMenu::item:selected {
            background-color: #2196F3;
        }

        /* ========================================
           DIALOGS
           ======================================== */

        QDialog {
            background-color: #2a2a2a;
            color: #e0e0e0;
        }

        QDialogButtonBox QPushButton {
            min-width: 80px;
            padding: 8px 16px;
        }
    """


def get_light_theme_stylesheet() -> str:
    """
    Return light theme stylesheet (for future use).
    Currently returns empty string - dark theme is default.
    """
    # TODO: Implement light theme if needed
    return ""


def get_custom_icons() -> dict:
    """
    Return dict of custom icon paths for the application.
    Can be used to load icon files or create custom SVG icons.
    """
    return {
        "refresh": "🔄",
        "folder": "📁",
        "drive": "☁️",
        "search": "🔍",
        "check": "✓",
        "cross": "✗",
        "play": "▶",
        "collapse": "▼",
        "expand": "▲",
        "success": "✓",
        "error": "✗",
        "warning": "⚠️",
        "info": "ℹ️",
    }