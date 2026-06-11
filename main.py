"""
main.py — HAC FAT & Inspection Management System
Entry point.
"""
import sys
import os

# ── Make sure project root is in sys.path ────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui     import QFont

from ui.shared.styles     import APP_STYLESHEET
from database.connection  import init_db, SessionLocal
from services.auth_service import AuthService


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)
    app.setFont(QFont("Segoe UI", 10))
    app.setApplicationName("HAC FAT System")

    # ── Init DB & ensure default admin exists ─────────────────────────────
    init_db()
    session = SessionLocal()
    AuthService(session).ensure_default_admin()

    # ── Login window ──────────────────────────────────────────────────────
    from ui.login_window import LoginWindow
    auth_svc   = AuthService(session)
    login_win  = LoginWindow(auth_svc)

    def on_login(user):
        login_win.hide()
        from ui.main_window import MainWindow
        main_win = MainWindow(user, session)
        main_win.show()
        # Keep reference alive
        app._main_win = main_win

    login_win.login_successful.connect(on_login)
    login_win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
