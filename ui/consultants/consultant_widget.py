"""ui/consultants/consultant_widget.py"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QDialog, QFormLayout, QTextEdit, QComboBox, QMessageBox,
    QAbstractItemView, QTabWidget,
)
from PyQt6.QtCore    import Qt
from config.settings import THEME as T
from models.consultant         import Consultant
from models.consultant_contact import ConsultantContact
from models.project            import Project


class ConsultantWidget(QWidget):
    def __init__(self, session, current_user, parent=None):
        super().__init__(parent)
        self.session = session
        self.current_user = current_user
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(14)

        hdr = QHBoxLayout()
        title = QLabel("Consultants")
        title.setStyleSheet(f"font-size:22px;font-weight:bold;color:{T['primary']};")
        hdr.addWidget(title); hdr.addStretch()
        add_btn = QPushButton("＋  Add Consultant")
        add_btn.setStyleSheet(f"background-color:{T['primary']}; color:white; font-weight:bold; padding:0 16px; border-radius:4px;")
        add_btn.setFixedHeight(34); add_btn.clicked.connect(self._add)
        
        self.edit_btn = QPushButton("✏️  Edit")
        self.edit_btn.setStyleSheet(f"background-color:{T['secondary']}; color:white; font-weight:bold; padding:0 16px; border-radius:4px;")
        self.edit_btn.setFixedHeight(34); self.edit_btn.clicked.connect(self._edit)
        self.edit_btn.setEnabled(False)
        
        self.del_btn = QPushButton("🗑  Delete")
        self.del_btn.setStyleSheet("background-color:#c0392b; color:white; font-weight:bold; padding:0 16px; border-radius:4px;")
        self.del_btn.setFixedHeight(34); self.del_btn.clicked.connect(self._delete)
        self.del_btn.setEnabled(False)
        
        hdr.addWidget(add_btn)
        hdr.addWidget(self.edit_btn)
        hdr.addWidget(self.del_btn)
        root.addLayout(hdr)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["#","Company Name","Notes"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.doubleClicked.connect(self._edit)
        root.addWidget(self.table)

    def _on_selection_changed(self):
        has_sel = len(self.table.selectedItems()) > 0
        self.edit_btn.setEnabled(has_sel)
        self.del_btn.setEnabled(has_sel)

    def refresh(self):
        consultants = self.session.query(Consultant).order_by(Consultant.company_name).all()
        self.table.setRowCount(len(consultants))
        for i, c in enumerate(consultants):
            self.table.setItem(i, 0, QTableWidgetItem(str(c.id)))
            self.table.setItem(i, 1, QTableWidgetItem(c.company_name or ""))
            self.table.setItem(i, 2, QTableWidgetItem(c.notes or ""))
            for col in range(3):
                if self.table.item(i, col):
                    self.table.item(i, col).setData(Qt.ItemDataRole.UserRole, c.id)

    def _add(self):
        dlg = ConsultantDialog(self.session, parent=self)
        if dlg.exec(): self.refresh()

    def _edit(self):
        row = self.table.currentRow()
        if row < 0: return
        cid = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        dlg = ConsultantDialog(self.session, cid, parent=self)
        if dlg.exec(): self.refresh()

    def _delete(self):
        row = self.table.currentRow()
        if row < 0: return
        cid = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        name = self.table.item(row, 1).text()
        reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete consultant '{name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                from models.consultant import Consultant
                c = self.session.get(Consultant, cid)
                if c:
                    self.session.delete(c)
                    self.session.commit()
                    self.refresh()
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Error", f"Cannot delete consultant because it is in use.\n\nDetails: {str(e)}")


class ConsultantDialog(QDialog):
    def __init__(self, session, consultant_id=None, parent=None):
        super().__init__(parent)
        self.session       = session
        self.consultant_id = consultant_id
        self.setWindowTitle("Consultant")
        self.setMinimumWidth(500)
        self._build_ui()
        if consultant_id: self._load()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        tabs = QTabWidget()

        # Info tab
        info = QWidget()
        form = QFormLayout(info)
        self.name_edit  = QLineEdit()
        self.notes_edit = QTextEdit(); self.notes_edit.setMaximumHeight(70)
        form.addRow("Company Name *", self.name_edit)
        form.addRow("Notes",          self.notes_edit)
        tabs.addTab(info, "Info")

        # Contacts tab
        contacts = QWidget()
        c_lay = QVBoxLayout(contacts)
        c_hdr = QHBoxLayout()
        add_con = QPushButton("＋  Add Contact")
        add_con.setStyleSheet(f"background-color:{T['secondary']}; color:white; font-weight:bold; padding:6px 12px; border-radius:4px;")
        add_con.clicked.connect(self._add_contact)
        
        self.edit_con_btn = QPushButton("✏️  Edit")
        self.edit_con_btn.setStyleSheet(f"background-color:{T['secondary']}; color:white; font-weight:bold; padding:6px 12px; border-radius:4px;")
        self.edit_con_btn.clicked.connect(self._edit_contact)
        self.edit_con_btn.setEnabled(False)
        
        self.del_con_btn = QPushButton("🗑  Delete")
        self.del_con_btn.setStyleSheet("background-color:#c0392b; color:white; font-weight:bold; padding:6px 12px; border-radius:4px;")
        self.del_con_btn.clicked.connect(self._delete_contact)
        self.del_con_btn.setEnabled(False)
        
        c_hdr.addStretch()
        c_hdr.addWidget(add_con)
        c_hdr.addWidget(self.edit_con_btn)
        c_hdr.addWidget(self.del_con_btn)
        c_lay.addLayout(c_hdr)

        self.contacts_table = QTableWidget()
        self.contacts_table.setColumnCount(5)
        self.contacts_table.setHorizontalHeaderLabels(["Name","Position","Mobile","Email","Project"])
        self.contacts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.contacts_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.contacts_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.contacts_table.setAlternatingRowColors(True)
        self.contacts_table.itemSelectionChanged.connect(self._on_contact_selection)
        self.contacts_table.doubleClicked.connect(self._edit_contact)
        c_lay.addWidget(self.contacts_table)
        tabs.addTab(contacts, "Contacts")

        lay.addWidget(tabs)
        btns = QHBoxLayout(); btns.addStretch()
        cancel = QPushButton("Cancel"); cancel.clicked.connect(self.reject)
        save   = QPushButton("Save")
        save.setStyleSheet(f"background:{T['primary']};color:white;border-radius:5px;padding:6px 20px;")
        save.clicked.connect(self._save)
        btns.addWidget(cancel); btns.addWidget(save)
        lay.addLayout(btns)

    def _on_contact_selection(self):
        has_sel = len(self.contacts_table.selectedItems()) > 0
        self.edit_con_btn.setEnabled(has_sel)
        self.del_con_btn.setEnabled(has_sel)

    def _load(self):
        c = self.session.get(Consultant, self.consultant_id)
        if not c: return
        self.name_edit.setText(c.company_name or "")
        self.notes_edit.setPlainText(c.notes or "")
        self._load_contacts()

    def _load_contacts(self):
        contacts = self.session.query(ConsultantContact).filter_by(consultant_id=self.consultant_id).all()
        self.contacts_table.setRowCount(len(contacts))
        for i, c in enumerate(contacts):
            proj = c.project.project_name if c.project else ""
            for j, v in enumerate([c.name, c.position or "", c.mobile or "", c.email or "", proj]):
                item = QTableWidgetItem(v)
                item.setData(Qt.ItemDataRole.UserRole, c.id)
                self.contacts_table.setItem(i, j, item)

    def _add_contact(self):
        if not self.consultant_id:
            QMessageBox.information(self, "Save First", "Please save the consultant first."); return
        dlg = ConsultantContactDialog(self.session, self.consultant_id, parent=self)
        if dlg.exec(): self._load_contacts()

    def _edit_contact(self):
        row = self.contacts_table.currentRow()
        if row < 0: return
        cid = self.contacts_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        dlg = ConsultantContactDialog(self.session, self.consultant_id, contact_id=cid, parent=self)
        if dlg.exec(): self._load_contacts()

    def _delete_contact(self):
        row = self.contacts_table.currentRow()
        if row < 0: return
        cid = self.contacts_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        name = self.contacts_table.item(row, 0).text()
        reply = QMessageBox.question(self, "Confirm Delete", f"Delete contact '{name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            c = self.session.get(ConsultantContact, cid)
            if c:
                self.session.delete(c)
                self.session.commit()
                self._load_contacts()

    def _save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Company name required."); return
        if self.consultant_id:
            c = self.session.get(Consultant, self.consultant_id)
        else:
            c = Consultant(); self.session.add(c)
        c.company_name = name
        c.notes        = self.notes_edit.toPlainText().strip() or None
        self.session.commit()
        self.consultant_id = c.id
        self.accept()


class ConsultantContactDialog(QDialog):
    def __init__(self, session, consultant_id, contact_id=None, parent=None):
        super().__init__(parent)
        self.session       = session
        self.consultant_id = consultant_id
        self.contact_id    = contact_id
        self.setWindowTitle("Consultant Contact")
        self.setMinimumWidth(400)
        self._build_ui()
        if contact_id: self._load()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        form = QFormLayout()
        self.name_edit     = QLineEdit()
        self.position_edit = QLineEdit()
        self.mobile_edit   = QLineEdit()
        self.email_edit    = QLineEdit()
        self.project_cb    = QComboBox()
        self.project_cb.addItem("— No specific project —", None)
        for p in self.session.query(Project).order_by(Project.project_name).all():
            self.project_cb.addItem(p.project_name, p.id)
        form.addRow("Name *",   self.name_edit)
        form.addRow("Position", self.position_edit)
        form.addRow("Mobile",   self.mobile_edit)
        form.addRow("Email",    self.email_edit)
        form.addRow("Project",  self.project_cb)
        lay.addLayout(form)
        btns = QHBoxLayout(); btns.addStretch()
        cancel = QPushButton("Cancel"); cancel.clicked.connect(self.reject)
        save   = QPushButton("Save")
        save.setStyleSheet(f"background:{T['primary']};color:white;border-radius:5px;padding:6px 20px;")
        save.clicked.connect(self._save)
        btns.addWidget(cancel); btns.addWidget(save)
        lay.addLayout(btns)

    def _load(self):
        c = self.session.get(ConsultantContact, self.contact_id)
        if not c: return
        self.name_edit.setText(c.name or "")
        self.position_edit.setText(c.position or "")
        self.mobile_edit.setText(c.mobile or "")
        self.email_edit.setText(c.email or "")
        for i in range(self.project_cb.count()):
            if self.project_cb.itemData(i) == c.project_id:
                self.project_cb.setCurrentIndex(i)

    def _save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Name required."); return
        if self.contact_id:
            c = self.session.get(ConsultantContact, self.contact_id)
        else:
            c = ConsultantContact(consultant_id=self.consultant_id); self.session.add(c)
        c.name       = name
        c.position   = self.position_edit.text().strip() or None
        c.mobile     = self.mobile_edit.text().strip() or None
        c.email      = self.email_edit.text().strip() or None
        c.project_id = self.project_cb.currentData()
        self.session.commit()
        self.accept()
