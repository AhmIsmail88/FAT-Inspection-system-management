"""ui/suppliers/contact_dialog.py"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton, QHBoxLayout, QMessageBox
from config.settings import THEME as T
from models.supplier_contact import SupplierContact
from models.project import Project


class SupplierContactDialog(QDialog):
    def __init__(self, session, supplier_id, contact_id=None, parent=None):
        super().__init__(parent)
        self.session     = session
        self.supplier_id = supplier_id
        self.contact_id  = contact_id
        self.setWindowTitle("Supplier Contact")
        self.setMinimumWidth(400)
        self._build_ui()
        if contact_id:
            self._load()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        form = QFormLayout()
        self.name_edit     = QLineEdit()
        self.position_edit = QLineEdit()
        self.mobile_edit   = QLineEdit()
        self.email_edit    = QLineEdit()
        self.whatsapp_edit = QLineEdit()
        self.project_cb    = QComboBox()
        self.project_cb.addItem("— No specific project —", None)
        for p in self.session.query(Project).order_by(Project.project_name).all():
            self.project_cb.addItem(p.project_name, p.id)
        form.addRow("Name *",    self.name_edit)
        form.addRow("Position",  self.position_edit)
        form.addRow("Mobile",    self.mobile_edit)
        form.addRow("Email",     self.email_edit)
        form.addRow("WhatsApp",  self.whatsapp_edit)
        form.addRow("Project",   self.project_cb)
        lay.addLayout(form)
        btns = QHBoxLayout(); btns.addStretch()
        cancel = QPushButton("Cancel"); cancel.clicked.connect(self.reject)
        save   = QPushButton("Save")
        save.setStyleSheet(f"background:{T['primary']};color:white;border-radius:5px;padding:6px 20px;")
        save.clicked.connect(self._save)
        btns.addWidget(cancel); btns.addWidget(save)
        lay.addLayout(btns)

    def _load(self):
        c = self.session.get(SupplierContact, self.contact_id)
        if not c: return
        self.name_edit.setText(c.name or "")
        self.position_edit.setText(c.position or "")
        self.mobile_edit.setText(c.mobile or "")
        self.email_edit.setText(c.email or "")
        self.whatsapp_edit.setText(c.whatsapp or "")
        for i in range(self.project_cb.count()):
            if self.project_cb.itemData(i) == c.project_id:
                self.project_cb.setCurrentIndex(i)

    def _save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Name is required.")
            return
        if self.contact_id:
            c = self.session.get(SupplierContact, self.contact_id)
        else:
            c = SupplierContact(supplier_id=self.supplier_id)
            self.session.add(c)
        c.name       = name
        c.position   = self.position_edit.text().strip() or None
        c.mobile     = self.mobile_edit.text().strip() or None
        c.email      = self.email_edit.text().strip() or None
        c.whatsapp   = self.whatsapp_edit.text().strip() or None
        c.project_id = self.project_cb.currentData()
        self.session.commit()
        self.accept()
