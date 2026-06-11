"""ui/shared/styles.py — HAC Corporate Theme"""
from config.settings import THEME as T

APP_STYLESHEET = f"""

/* ══════════════════════════════════════════════
   GLOBAL
══════════════════════════════════════════════ */
QWidget {{
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
    color: {T['text']};
    background-color: {T['bg']};
}}

QMainWindow {{
    background-color: {T['bg']};
}}

/* ══════════════════════════════════════════════
   INPUT FIELDS  (single definition — no conflicts)
══════════════════════════════════════════════ */
QLineEdit, QTextEdit, QDateEdit, QSpinBox, QDoubleSpinBox {{
    background-color: white;
    border: 1px solid {T['border']};
    border-radius: 5px;
    padding: 6px 10px;
    font-size: 13px;
    color: {T['text']};
    selection-background-color: {T['secondary']};
    selection-color: white;
}}
QLineEdit:focus, QTextEdit:focus, QDateEdit:focus,
QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 2px solid {T['primary']};
    background-color: white;
}}
QLineEdit:disabled, QTextEdit:disabled {{
    background-color: #f1f3f5;
    color: #95a5a6;
}}

/* ── ComboBox (separate — needs drop-down styling) ── */
QComboBox {{
    background-color: white;
    border: 1px solid {T['border']};
    border-radius: 5px;
    padding: 6px 10px;
    font-size: 13px;
    color: {T['text']};
}}
QComboBox:focus {{
    border: 2px solid {T['primary']};
}}
QComboBox:disabled {{
    background-color: #f1f3f5;
    color: #95a5a6;
}}
QComboBox::drop-down {{
    border: none;
    padding-right: 10px;
    width: 20px;
}}
QComboBox QAbstractItemView {{
    background: white;
    border: 1px solid {T['border']};
    selection-background-color: {T['secondary']};
    selection-color: white;
    outline: none;
}}

/* ── Search bar override ── */
QLineEdit#search_bar {{
    border: 1px solid {T['border']};
    border-radius: 20px;
    padding: 6px 16px;
    background-color: white;
    font-size: 13px;
    min-width: 280px;
}}
QLineEdit#search_bar:focus {{
    border: 2px solid {T['secondary']};
}}

/* ══════════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════════ */
QPushButton {{
    background-color: {T['primary']};
    color: white;
    border: none;
    padding: 7px 18px;
    border-radius: 5px;
    font-size: 13px;
    font-weight: bold;
}}
QPushButton:hover   {{ background-color: {T['secondary']}; }}
QPushButton:pressed {{ background-color: #0d2b45; }}
QPushButton:disabled {{
    background-color: #bdc3c7;
    color: #7f8c8d;
}}

/* ══════════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════════ */
QFrame#sidebar {{
    background-color: {T['sidebar_bg']};
    border-right: 1px solid #0d2b45;
}}
QFrame#sidebar QPushButton {{
    background-color: transparent;
    color: {T['sidebar_text']};
    border: none;
    padding: 13px 20px;
    text-align: left;
    font-size: 13px;
    font-weight: normal;
    border-radius: 0px;
}}
QFrame#sidebar QPushButton:hover {{
    background-color: {T['sidebar_hover']};
}}
QFrame#sidebar QPushButton:checked {{
    background-color: {T['secondary']};
    border-left: 4px solid {T['accent']};
    font-weight: bold;
}}

/* ══════════════════════════════════════════════
   TABLES
══════════════════════════════════════════════ */
QTableWidget {{
    background-color: white;
    gridline-color: {T['border']};
    border: 1px solid {T['border']};
    border-radius: 6px;
    selection-background-color: #d6e8f7;
    selection-color: {T['text']};
    alternate-background-color: #f9fafc;
    outline: none;
}}
QTableWidget::item {{
    padding: 5px 10px;
    border: none;
}}
QTableWidget::item:selected {{
    background-color: #d6e8f7;
    color: {T['text']};
}}
QHeaderView::section {{
    background-color: {T['primary']};
    color: white;
    padding: 8px 10px;
    border: none;
    font-weight: bold;
    font-size: 12px;
}}
QHeaderView::section:hover {{
    background-color: {T['secondary']};
}}

/* ══════════════════════════════════════════════
   DIALOGS & FORMS
══════════════════════════════════════════════ */
QDialog {{
    background-color: {T['surface']};
}}
QGroupBox {{
    border: 1px solid {T['border']};
    border-radius: 6px;
    margin-top: 14px;
    padding-top: 10px;
    font-weight: bold;
    color: {T['primary']};
    background: white;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    background: white;
}}

/* ══════════════════════════════════════════════
   TABS
══════════════════════════════════════════════ */
QTabWidget::pane {{
    border: 1px solid {T['border']};
    border-radius: 0 6px 6px 6px;
    background: white;
}}
QTabBar::tab {{
    background: #dce8f5;
    color: {T['text']};
    padding: 8px 20px;
    border-radius: 4px 4px 0 0;
    margin-right: 2px;
    font-size: 13px;
}}
QTabBar::tab:selected {{
    background: {T['primary']};
    color: white;
    font-weight: bold;
}}
QTabBar::tab:hover:!selected {{
    background: #b8d4ed;
}}

/* ══════════════════════════════════════════════
   SCROLLBARS
══════════════════════════════════════════════ */
QScrollBar:vertical {{
    background: {T['bg']};
    width: 8px;
    border-radius: 4px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: #c0cdd8;
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {T['secondary']};
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{ height: 0; border: none; }}
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{ background: none; }}

QScrollBar:horizontal {{
    background: {T['bg']};
    height: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: #c0cdd8;
    border-radius: 4px;
    min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {T['secondary']};
}}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{ width: 0; border: none; }}

/* ══════════════════════════════════════════════
   MISC
══════════════════════════════════════════════ */
QToolTip {{
    background-color: {T['primary']};
    color: white;
    border: none;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}}
QMessageBox {{
    background-color: white;
}}
QMessageBox QPushButton {{
    min-width: 80px;
    min-height: 30px;
}}
QSplitter::handle {{
    background: {T['border']};
}}
"""
