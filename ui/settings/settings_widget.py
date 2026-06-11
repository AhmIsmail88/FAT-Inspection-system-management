"""ui/settings/settings_widget.py"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QComboBox, QMessageBox, QTabWidget,
    QAbstractItemView, QCheckBox,
)
from PyQt6.QtCore    import Qt
from config.settings import THEME as T, ROLES
from models.user     import User
from models.audit_log import AuditLog
from ui.settings.audit_details_dialog import AuditDetailsDialog


class SettingsWidget(QWidget):
    def __init__(self, session, current_user, parent=None):
        super().__init__(parent)
        self.session      = session
        self.current_user = current_user
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(14)

        title = QLabel("Settings")
        title.setStyleSheet(f"font-size:22px;font-weight:bold;color:{T['primary']};")
        root.addWidget(title)

        tabs = QTabWidget()

        # ── User Management ────────────────────────────────────────────────
        users_tab = QWidget()
        u_lay = QVBoxLayout(users_tab)
        u_hdr = QHBoxLayout()
        add_user_btn = QPushButton("＋  Add User")
        add_user_btn.setFixedHeight(34)
        add_user_btn.clicked.connect(self._add_user)
        u_hdr.addStretch(); u_hdr.addWidget(add_user_btn)
        u_lay.addLayout(u_hdr)

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels(["#","Username","Full Name","Role","Active"])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.users_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.users_table.setAlternatingRowColors(True)
        self.users_table.doubleClicked.connect(self._edit_user)
        u_lay.addWidget(self.users_table)
        tabs.addTab(users_tab, "👤  Users")

        # ── Change Password ────────────────────────────────────────────────
        pwd_tab = QWidget()
        p_lay = QVBoxLayout(pwd_tab)
        p_lay.setContentsMargins(30, 30, 30, 30)

        form = QFormLayout()
        self.old_pwd   = QLineEdit(); self.old_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pwd   = QLineEdit(); self.new_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.conf_pwd  = QLineEdit(); self.conf_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Current Password", self.old_pwd)
        form.addRow("New Password",     self.new_pwd)
        form.addRow("Confirm Password", self.conf_pwd)
        p_lay.addLayout(form)
        p_lay.addSpacing(12)

        change_btn = QPushButton("Change Password")
        change_btn.setFixedHeight(38)
        change_btn.setFixedWidth(180)
        change_btn.setStyleSheet(f"background:{T['primary']};color:white;border-radius:5px;")
        change_btn.clicked.connect(self._change_password)
        p_lay.addWidget(change_btn)
        p_lay.addStretch()
        tabs.addTab(pwd_tab, "🔑  Change Password")

        # ── Database Path ──────────────────────────────────────────────────
        db_tab = QWidget()
        db_lay = QVBoxLayout(db_tab)
        db_lay.setContentsMargins(30, 30, 30, 30)
        db_lay.setSpacing(14)

        from config.settings import get_current_db_path_label
        db_title = QLabel("Database Location")
        db_title.setStyleSheet(f"font-size:14px; font-weight:bold; color:{T['primary']};")
        db_lay.addWidget(db_title)

        db_info = QLabel(
            "The database folder stores fat_system.db and all attachments.\n"
            "Change this path if the server location has moved."
        )
        db_info.setWordWrap(True)
        db_info.setStyleSheet(f"color:{T['text_light']}; font-size:12px;")
        db_lay.addWidget(db_info)

        self.db_path_display = QLineEdit()
        self.db_path_display.setText(get_current_db_path_label())
        self.db_path_display.setReadOnly(True)
        self.db_path_display.setFixedHeight(38)
        self.db_path_display.setStyleSheet(
            f"background:#f8f9fa; border:1px solid {T['border']};"
            f" border-radius:5px; padding:0 10px; color:{T['text']};"
        )
        db_lay.addWidget(self.db_path_display)

        change_db_btn = QPushButton("⚙️  Change Database Path")
        change_db_btn.setFixedHeight(40)
        change_db_btn.setFixedWidth(220)
        change_db_btn.setStyleSheet(
            f"background:{T['primary']}; color:white; border-radius:5px;"
            f" font-size:13px;"
        )
        change_db_btn.clicked.connect(self._change_db_path)
        db_lay.addWidget(change_db_btn)
        db_lay.addStretch()
        tabs.addTab(db_tab, "🗄️  Database")

        # ── Audit Logs ───────────────────────────────────────────────────
        audit_tab = QWidget()
        a_lay = QVBoxLayout(audit_tab)
        a_lay.setContentsMargins(10, 10, 10, 10)

        self.audit_table = QTableWidget()
        self.audit_table.setColumnCount(6)
        self.audit_table.setHorizontalHeaderLabels(["ID", "Date/Time", "User", "Action", "Table (Record)", "Details"])
        self.audit_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.audit_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.audit_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.audit_table.setAlternatingRowColors(True)
        a_lay.addWidget(self.audit_table)
        tabs.addTab(audit_tab, "📝  Audit Logs")

        root.addWidget(tabs)

    def refresh(self):
        self._load_users()
        self._load_audit_logs()

    def _load_audit_logs(self):
        # Fetch last 200 logs
        logs = self.session.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(200).all()
        self.audit_table.setRowCount(len(logs))
        for i, log in enumerate(logs):
            self.audit_table.setItem(i, 0, QTableWidgetItem(str(log.id)))
            self.audit_table.setItem(i, 1, QTableWidgetItem(log.created_at.strftime("%Y-%m-%d %H:%M:%S")))
            
            username = log.user.username if log.user else f"Unknown ({log.user_id})"
            self.audit_table.setItem(i, 2, QTableWidgetItem(username))
            
            self.audit_table.setItem(i, 3, QTableWidgetItem(log.action))
            self.audit_table.setItem(i, 4, QTableWidgetItem(f"{log.table_name} (#{log.record_id})"))
            
            btn = QPushButton("View Details")
            btn.setStyleSheet(f"background-color: {T['secondary']}; color: white; padding: 4px; border-radius: 4px;")
            btn.clicked.connect(lambda checked, a=log.action, o=log.old_value, n=log.new_value: self._show_audit_details(a, o, n))
            
            w = QWidget()
            l = QHBoxLayout(w)
            l.setContentsMargins(0,0,0,0)
            l.addWidget(btn)
            self.audit_table.setCellWidget(i, 5, w)
            
        self.audit_table.resizeColumnsToContents()

    def _show_audit_details(self, action, old_val, new_val):
        dlg = AuditDetailsDialog(action, old_val, new_val, parent=self)
        dlg.exec()

    def _load_users(self):
        users = self.session.query(User).order_by(User.username).all()
        self.users_table.setRowCount(len(users))
        for i, u in enumerate(users):
            self.users_table.setItem(i, 0, QTableWidgetItem(str(u.id)))
            self.users_table.setItem(i, 1, QTableWidgetItem(u.username))
            self.users_table.setItem(i, 2, QTableWidgetItem(u.full_name or ""))
            self.users_table.setItem(i, 3, QTableWidgetItem(u.role))
            self.users_table.setItem(i, 4, QTableWidgetItem("✓ Active" if u.is_active else "✗ Inactive"))
            for c in range(5):
                if self.users_table.item(i, c):
                    self.users_table.item(i, c).setData(Qt.ItemDataRole.UserRole, u.id)

    def _add_user(self):
        dlg = UserDialog(self.session, parent=self)
        if dlg.exec(): self._load_users()

    def _edit_user(self):
        row = self.users_table.currentRow()
        if row < 0: return
        uid = self.users_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        dlg = UserDialog(self.session, uid, parent=self)
        if dlg.exec(): self._load_users()

    def _change_db_path(self):
        from ui.shared.db_path_dialog import DBPathDialog
        from config.settings import get_current_db_path_label
        dlg = DBPathDialog(parent=self)
        if dlg.exec():
            self.db_path_display.setText(get_current_db_path_label())

    def _change_password(self):
        from services.auth_service import AuthService
        svc = AuthService(self.session)
        old = self.old_pwd.text()
        new = self.new_pwd.text()
        conf= self.conf_pwd.text()
        if not svc.login(self.current_user.username, old):
            QMessageBox.warning(self, "Error", "Current password is incorrect."); return
        if new != conf:
            QMessageBox.warning(self, "Error", "New passwords do not match."); return
        if len(new) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters."); return
        svc.change_password(self.current_user.id, new)
        self.old_pwd.clear(); self.new_pwd.clear(); self.conf_pwd.clear()
        QMessageBox.information(self, "Success", "Password changed successfully.")


class UserDialog(QDialog):
    def __init__(self, session, user_id=None, parent=None):
        super().__init__(parent)
        self.session = session
        self.user_id = user_id
        self.setWindowTitle("Edit User" if user_id else "Add User")
        self.setMinimumWidth(380)
        self._build_ui()
        if user_id: self._load()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        form = QFormLayout()
        self.username_edit  = QLineEdit()
        self.fullname_edit  = QLineEdit()
        self.role_cb        = QComboBox(); self.role_cb.addItems(ROLES)
        self.active_cb      = QCheckBox("Active"); self.active_cb.setChecked(True)
        self.password_edit  = QLineEdit(); self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        if self.user_id:
            self.password_edit.setPlaceholderText("Leave blank to keep current")
        form.addRow("Username *",  self.username_edit)
        form.addRow("Full Name",   self.fullname_edit)
        form.addRow("Role",        self.role_cb)
        form.addRow("Status",      self.active_cb)
        form.addRow("Password",    self.password_edit)
        lay.addLayout(form)
        btns = QHBoxLayout(); btns.addStretch()
        cancel = QPushButton("Cancel"); cancel.clicked.connect(self.reject)
        save   = QPushButton("Save")
        save.setStyleSheet(f"background:{T['primary']};color:white;border-radius:5px;padding:6px 20px;")
        save.clicked.connect(self._save)
        btns.addWidget(cancel); btns.addWidget(save)
        lay.addLayout(btns)

    def _load(self):
        u = self.session.get(User, self.user_id)
        if not u: return
        self.username_edit.setText(u.username)
        self.fullname_edit.setText(u.full_name or "")
        self.role_cb.setCurrentText(u.role)
        self.active_cb.setChecked(u.is_active)

    def _save(self):
        username = self.username_edit.text().strip()
        if not username:
            QMessageBox.warning(self, "Validation", "Username is required."); return
        if self.user_id:
            u = self.session.get(User, self.user_id)
        else:
            if not self.password_edit.text():
                QMessageBox.warning(self, "Validation", "Password is required for new users."); return
            u = User(); self.session.add(u)
        u.username  = username
        u.full_name = self.fullname_edit.text().strip() or None
        u.role      = self.role_cb.currentText()
        u.is_active = self.active_cb.isChecked()
        if self.password_edit.text():
            u.password_hash = User.hash_password(self.password_edit.text())
        self.session.commit()
        self.accept()
