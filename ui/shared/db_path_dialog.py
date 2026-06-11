"""
ui/shared/db_path_dialog.py
────────────────────────────
Reusable dialog for changing the database path.
Used in:
  - Login screen  (before connecting)
  - Settings page (after login, Admin only)
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QFileDialog, QMessageBox,
)
from PyQt6.QtCore import Qt
from config.settings import THEME as T, get_current_db_path_label, set_db_path


class DBPathDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Database Settings")
        self.setFixedWidth(500)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────
        header = QLabel("  🗄️  Database Path Settings")
        header.setFixedHeight(48)
        header.setStyleSheet(
            f"background:{T['primary']}; color:white;"
            f" font-size:14px; font-weight:bold; padding-left:16px;"
        )
        root.addWidget(header)

        # ── Body ──────────────────────────────────────────────────────────
        body = QFrame()
        body.setStyleSheet("background:white;")
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(24, 20, 24, 20)
        body_lay.setSpacing(14)

        # Info box
        info = QLabel(
            "The database folder contains <b>fat_system.db</b> and all attachments.<br>"
            "This is usually located on the company server."
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            f"background:#eaf4ff; border:1px solid #b8d4ed; border-radius:6px;"
            f" padding:10px; color:{T['text']}; font-size:12px;"
        )
        body_lay.addWidget(info)

        # Current path label
        current_lbl = QLabel("Current database path:")
        current_lbl.setStyleSheet(
            f"color:{T['text_light']}; font-size:11px; font-weight:bold;"
        )
        body_lay.addWidget(current_lbl)

        # Path display + Browse row
        path_row = QHBoxLayout()
        path_row.setSpacing(8)

        self.path_input = QLineEdit()
        self.path_input.setText(get_current_db_path_label())
        self.path_input.setReadOnly(True)
        self.path_input.setFixedHeight(38)
        self.path_input.setStyleSheet(
            f"border:1px solid {T['border']}; border-radius:5px;"
            f" padding:0 10px; background:#f8f9fa; color:{T['text']};"
            f" font-size:12px;"
        )
        path_row.addWidget(self.path_input)

        browse_btn = QPushButton("Browse…")
        browse_btn.setFixedHeight(38)
        browse_btn.setFixedWidth(90)
        browse_btn.setStyleSheet(
            f"background:{T['secondary']}; color:white; border-radius:5px;"
            f" font-size:12px; font-weight:bold;"
        )
        browse_btn.clicked.connect(self._browse)
        path_row.addWidget(browse_btn)
        body_lay.addLayout(path_row)

        # Restart warning
        self.warning_lbl = QLabel(
            "⚠️  A restart is required for the new path to take effect."
        )
        self.warning_lbl.setStyleSheet(
            "color:#e67e22; font-size:12px; font-weight:bold;"
        )
        self.warning_lbl.setVisible(False)
        body_lay.addWidget(self.warning_lbl)

        root.addWidget(body)

        # ── Footer buttons ────────────────────────────────────────────────
        footer = QFrame()
        footer.setStyleSheet(
            f"background:{T['bg']}; border-top:1px solid {T['border']};"
        )
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(20, 10, 20, 10)
        f_lay.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(36)
        cancel_btn.setStyleSheet(
            "background:#95a5a6; color:white; border-radius:5px; padding:0 18px;"
        )
        cancel_btn.clicked.connect(self.reject)

        self.save_btn = QPushButton("Save & Restart")
        self.save_btn.setFixedHeight(36)
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet(
            f"background:{T['primary']}; color:white; border-radius:5px;"
            f" padding:0 18px; font-weight:bold;"
        )
        self.save_btn.clicked.connect(self._save)

        f_lay.addWidget(cancel_btn)
        f_lay.addWidget(self.save_btn)
        root.addWidget(footer)

        self._new_path = None

    # ── Browse ────────────────────────────────────────────────────────────
    def _browse(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Database Folder",
            self.path_input.text(),
        )
        if not folder:
            return

        self._new_path = folder
        self.path_input.setText(folder)
        self.warning_lbl.setVisible(True)
        self.save_btn.setEnabled(True)

    # ── Save ──────────────────────────────────────────────────────────────
    def _save(self):
        if not self._new_path:
            return

        set_db_path(self._new_path)

        QMessageBox.information(
            self,
            "Path Saved",
            f"Database path updated to:\n{self._new_path}\n\n"
            "Please close and reopen the application for the change to take effect.",
        )
        self.accept()
