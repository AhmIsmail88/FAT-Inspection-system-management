"""ui/login_window.py — HAC Login Screen"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui  import QPixmap

from config.settings import (
    COMPANY_NAME, DESIGNED_BY, FOOTER_TEXT,
    LOGO_PATH, THEME as T, get_current_db_path_label,
)


class LoginWindow(QWidget):
    login_successful = pyqtSignal(object)

    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle(f"{COMPANY_NAME} — FAT System")
        self.setFixedSize(440, 640)
        self.setStyleSheet(f"background-color: {T['bg']};")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────
        header = QFrame()
        header.setFixedHeight(180)
        header.setStyleSheet(f"background-color: {T['sidebar_bg']};")
        h_lay = QVBoxLayout(header)
        h_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_lay.setSpacing(4)

        logo_lbl = QLabel()
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_lbl.setStyleSheet("background: transparent;")
        if LOGO_PATH.exists():
            pix = QPixmap(str(LOGO_PATH)).scaledToWidth(
                160, Qt.TransformationMode.SmoothTransformation
            )
            logo_lbl.setPixmap(pix)
        else:
            logo_lbl.setText(COMPANY_NAME)
            logo_lbl.setStyleSheet(
                f"color:{T['primary']}; font-size:26px;"
                f" font-weight:bold; background:transparent;"
            )
        h_lay.addWidget(logo_lbl)
        root.addWidget(header)

        # ── Card ──────────────────────────────────────────────────────────
        card = QFrame()
        card.setStyleSheet("background-color: white;")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(40, 28, 40, 28)
        card_lay.setSpacing(10)

        title = QLabel("Sign In")
        title.setStyleSheet(
            f"font-size:22px; font-weight:bold; color:{T['primary']};"
            f" background:transparent;"
        )
        card_lay.addWidget(title)

        subtitle = QLabel("FAT & Inspection Management System")
        subtitle.setStyleSheet(
            f"color:{T['text_light']}; font-size:12px; background:transparent;"
        )
        card_lay.addWidget(subtitle)

        card_lay.addSpacing(12)

        # ── Username ──────────────────────────────────────────────────────
        user_lbl = QLabel("Username")
        user_lbl.setStyleSheet(
            f"color:{T['text']}; font-size:12px; font-weight:bold; background:transparent;"
        )
        card_lay.addWidget(user_lbl)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setFixedHeight(42)
        self.username_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {T['border']};
                border-radius: 5px;
                padding: 0 12px;
                font-size: 13px;
                background: white;
                color: {T['text']};
            }}
            QLineEdit:focus {{ border: 2px solid {T['primary']}; }}
        """)
        self.username_input.returnPressed.connect(self._do_login)
        card_lay.addWidget(self.username_input)

        card_lay.addSpacing(6)

        # ── Password ──────────────────────────────────────────────────────
        pass_lbl = QLabel("Password")
        pass_lbl.setStyleSheet(
            f"color:{T['text']}; font-size:12px; font-weight:bold; background:transparent;"
        )
        card_lay.addWidget(pass_lbl)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(42)
        self.password_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {T['border']};
                border-radius: 5px;
                padding: 0 12px;
                font-size: 13px;
                background: white;
                color: {T['text']};
            }}
            QLineEdit:focus {{ border: 2px solid {T['primary']}; }}
        """)
        self.password_input.returnPressed.connect(self._do_login)
        card_lay.addWidget(self.password_input)

        # ── Error label ───────────────────────────────────────────────────
        self.error_lbl = QLabel("")
        self.error_lbl.setStyleSheet(
            "color:#e74c3c; font-size:12px; background:transparent;"
        )
        self.error_lbl.setVisible(False)
        card_lay.addWidget(self.error_lbl)

        card_lay.addSpacing(14)

        # ── Sign In button ────────────────────────────────────────────────
        login_btn = QPushButton("Sign In")
        login_btn.setFixedHeight(46)
        login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {T['primary']};
                color: white; border: none;
                border-radius: 6px;
                font-size: 14px; font-weight: bold;
            }}
            QPushButton:hover   {{ background-color: {T['secondary']}; }}
            QPushButton:pressed {{ background-color: #0d2b45; }}
        """)
        login_btn.clicked.connect(self._do_login)
        card_lay.addWidget(login_btn)

        root.addWidget(card)

        # ── DB path bar ───────────────────────────────────────────────────
        db_bar = QFrame()
        db_bar.setStyleSheet(
            f"background:#eef2f7; border-top:1px solid {T['border']};"
        )
        db_lay = QHBoxLayout(db_bar)
        db_lay.setContentsMargins(16, 8, 16, 8)
        db_lay.setSpacing(8)

        db_icon = QLabel("🗄️")
        db_icon.setStyleSheet("background:transparent; font-size:14px;")
        db_lay.addWidget(db_icon)

        self.db_path_lbl = QLabel(self._short_path(get_current_db_path_label()))
        self.db_path_lbl.setStyleSheet(
            f"color:{T['text_light']}; font-size:11px; background:transparent;"
        )
        self.db_path_lbl.setToolTip(get_current_db_path_label())
        db_lay.addWidget(self.db_path_lbl, 1)

        db_settings_btn = QPushButton("⚙️  Change")
        db_settings_btn.setFixedHeight(28)
        db_settings_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {T['secondary']};
                border: 1px solid {T['secondary']};
                border-radius: 4px;
                font-size: 11px;
                padding: 0 10px;
                font-weight: normal;
            }}
            QPushButton:hover {{
                background: {T['secondary']};
                color: white;
            }}
        """)
        db_settings_btn.clicked.connect(self._open_db_settings)
        db_lay.addWidget(db_settings_btn)

        root.addWidget(db_bar)

        # ── Footer ────────────────────────────────────────────────────────
        footer = QFrame()
        footer.setStyleSheet(f"background-color:{T['primary']};")
        f_lay = QVBoxLayout(footer)
        f_lay.setContentsMargins(10, 8, 10, 10)
        f_lay.setSpacing(3)

        dua_lbl = QLabel(FOOTER_TEXT)
        dua_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dua_lbl.setStyleSheet("color:#aed6f1; font-size:12px; background:transparent;")
        f_lay.addWidget(dua_lbl)

        by_lbl = QLabel(DESIGNED_BY)
        by_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        by_lbl.setStyleSheet("color:#7fb3d3; font-size:10px; background:transparent;")
        f_lay.addWidget(by_lbl)

        root.addWidget(footer)

    # ── Helpers ───────────────────────────────────────────────────────────
    def _short_path(self, path: str, max_len: int = 45) -> str:
        if len(path) <= max_len:
            return path
        return "…" + path[-(max_len - 1):]

    def _open_db_settings(self):
        from ui.shared.db_path_dialog import DBPathDialog
        dlg = DBPathDialog(parent=self)
        if dlg.exec():
            # Refresh the displayed path
            self.db_path_lbl.setText(
                self._short_path(get_current_db_path_label())
            )
            self.db_path_lbl.setToolTip(get_current_db_path_label())

    def _do_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self._show_error("Please enter username and password")
            return

        user = self.auth_service.login(username, password)
        if user:
            self.login_successful.emit(user)
        else:
            self._show_error("Invalid username or password")
            self.password_input.clear()
            self.password_input.setFocus()

    def _show_error(self, msg: str):
        self.error_lbl.setText(f"⚠  {msg}")
        self.error_lbl.setVisible(True)
