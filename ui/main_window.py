"""ui/main_window.py — HAC Main Window with Sidebar"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui  import QPixmap, QIcon

from config.settings import APP_NAME, COMPANY_NAME, DESIGNED_BY, FOOTER_TEXT, LOGO_PATH, THEME as T


NAV_ITEMS = [
    ("dashboard",   "📊",  "Dashboard"),
    ("fat",         "📋",  "FAT Records"),
    ("projects",    "🏗️",  "Projects"),
    ("suppliers",   "🏭",  "Suppliers"),
    ("consultants", "👔",  "Consultants"),
    ("reports",     "📄",  "Reports"),
    ("settings",    "⚙️",  "Settings"),
]


class SidebarButton(QPushButton):
    def __init__(self, icon: str, label: str, parent=None):
        super().__init__(f"  {icon}  {label}", parent)
        self.setCheckable(True)
        self.setFixedHeight(46)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class MainWindow(QMainWindow):
    def __init__(self, current_user, session):
        super().__init__()
        self.current_user = current_user
        self.session      = session
        self._pages       = {}
        self._nav_buttons = {}
        self._build_ui()
        self._load_pages()
        self._navigate("dashboard")

    # ── Build skeleton ────────────────────────────────────────────────────
    def _build_ui(self):
        self.setWindowTitle(f"{COMPANY_NAME} — FAT & Inspection System")
        self.setMinimumSize(1280, 780)
        self.showMaximized()

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top bar ───────────────────────────────────────────────────────
        top_bar = QFrame()
        top_bar.setFixedHeight(50)
        top_bar.setStyleSheet(f"background-color: {T['primary']}; border-bottom: 2px solid {T['accent']};")
        top_lay = QHBoxLayout(top_bar)
        top_lay.setContentsMargins(16, 0, 16, 0)

        app_lbl = QLabel(APP_NAME)
        app_lbl.setStyleSheet("color: white; font-size: 15px; font-weight: bold;")
        top_lay.addWidget(app_lbl)
        top_lay.addStretch()

        self.user_lbl = QLabel(f"👤  {self.current_user.full_name or self.current_user.username}  [{self.current_user.role}]")
        self.user_lbl.setStyleSheet("color: #aed6f1; font-size: 12px;")
        top_lay.addWidget(self.user_lbl)

        logout_btn = QPushButton("Sign Out")
        logout_btn.setFixedHeight(30)
        logout_btn.setStyleSheet("""
            QPushButton { background: transparent; color: #e74c3c;
                          border: 1px solid #e74c3c; border-radius: 4px; padding: 0 12px; }
            QPushButton:hover { background: #e74c3c; color: white; }
        """)
        logout_btn.clicked.connect(self._logout)
        top_lay.addWidget(logout_btn)
        root.addWidget(top_bar)

        # ── Body (sidebar + content) ──────────────────────────────────────
        body = QWidget()
        body_lay = QHBoxLayout(body)
        body_lay.setContentsMargins(0, 0, 0, 0)
        body_lay.setSpacing(0)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(210)
        sidebar_lay = QVBoxLayout(self.sidebar)
        sidebar_lay.setContentsMargins(0, 0, 0, 0)
        sidebar_lay.setSpacing(0)

        # Logo area in sidebar
        logo_frame = QFrame()
        logo_frame.setFixedHeight(190)
        logo_frame.setStyleSheet(f"background-color: {T['sidebar_bg']};")
        logo_lay = QVBoxLayout(logo_frame)
        logo_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_lbl = QLabel()
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if LOGO_PATH.exists():
            pix = QPixmap(str(LOGO_PATH)).scaledToWidth(120, Qt.TransformationMode.SmoothTransformation)
            logo_lbl.setPixmap(pix)
        else:
            logo_lbl.setText("") # Clear the placeholder text since we use the logo image itself
            logo_lbl.setText("")
        logo_lay.addWidget(logo_lbl)

        company_lbl = QLabel(COMPANY_NAME)
        company_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        company_lbl.setStyleSheet(f"color: {T['primary']}; font-size: 15px; font-weight: bold;")
        logo_lay.addWidget(company_lbl)

        sub_lbl = QLabel("FAT & Inspection")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_lbl.setStyleSheet(f"color: {T['text_light']}; font-size: 11px;")
        sub_lbl.hide() # Hide the subtitle since the logo image has the subtitle text
        logo_lay.addWidget(sub_lbl)
        sidebar_lay.addWidget(logo_frame)

        # Main Nav Buttons
        self._nav_buttons = {}
        for key, icon, label in NAV_ITEMS:
            if key == "settings" and self.current_user.role != "Admin":
                continue
            btn = SidebarButton(icon, label)
            btn.clicked.connect(lambda checked, k=key: self._navigate(k))
            self.sidebar.layout().addWidget(btn)
            self._nav_buttons[key] = btn

        sidebar_lay.addStretch()

        ver_lbl = QLabel(f"v1.0.0")
        ver_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver_lbl.setStyleSheet(f"color: {T['text_light']}; font-size: 10px; padding: 6px;")
        sidebar_lay.addWidget(ver_lbl)

        body_lay.addWidget(self.sidebar)

        # Content stack
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {T['bg']};")
        body_lay.addWidget(self.stack)

        root.addWidget(body)

        # ── Footer ────────────────────────────────────────────────────────
        footer = QFrame()
        footer.setFixedHeight(28)
        footer.setStyleSheet(f"background-color: {T['primary']};")
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(16, 0, 16, 0)

        dua = QLabel(FOOTER_TEXT)
        dua.setStyleSheet("color: #aed6f1; font-size: 11px;")
        f_lay.addWidget(dua)
        f_lay.addStretch()

        designed = QLabel(DESIGNED_BY)
        designed.setStyleSheet("color: #7fb3d3; font-size: 10px;")
        f_lay.addWidget(designed)
        root.addWidget(footer)

    # ── Load pages lazily ─────────────────────────────────────────────────
    def _load_pages(self):
        from ui.dashboard.dashboard_widget  import DashboardWidget
        from ui.fat.fat_table_widget        import FATTableWidget
        from ui.projects.project_widget     import ProjectWidget
        from ui.suppliers.supplier_widget   import SupplierWidget
        from ui.consultants.consultant_widget import ConsultantWidget
        from ui.reports.reports_widget      import ReportsWidget

        self._pages = {
            "dashboard":   DashboardWidget(self.session, self.current_user),
            "fat":         FATTableWidget(self.session, self.current_user),
            "projects":    ProjectWidget(self.session, self.current_user),
            "suppliers":   SupplierWidget(self.session, self.current_user),
            "consultants": ConsultantWidget(self.session, self.current_user),
            "reports":     ReportsWidget(self.session, self.current_user),
        }

        if self.current_user.role == "Admin":
            from ui.settings.settings_widget import SettingsWidget
            self._pages["settings"] = SettingsWidget(self.session, self.current_user)

        for page in self._pages.values():
            self.stack.addWidget(page)

    # ── Navigation ────────────────────────────────────────────────────────
    def _navigate(self, key: str):
        # Uncheck all
        for btn in self._nav_buttons.values():
            btn.setChecked(False)

        if key in self._nav_buttons:
            self._nav_buttons[key].setChecked(True)

        if key in self._pages:
            page = self._pages[key]
            self.stack.setCurrentWidget(page)
            # Refresh data if page supports it
            if hasattr(page, "refresh"):
                page.refresh()

    def _logout(self):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Sign Out", "Are you sure you want to sign out?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
