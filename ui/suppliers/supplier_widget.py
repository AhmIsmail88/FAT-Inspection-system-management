"""ui/suppliers/supplier_widget.py"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QDialog, QFormLayout, QTextEdit, QMessageBox, QAbstractItemView,
    QTabWidget, QGroupBox,
)
from PyQt6.QtCore import Qt
from config.settings    import THEME as T
from models.supplier    import Supplier
from models.supplier_contact import SupplierContact


class SupplierWidget(QWidget):
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
        title = QLabel("Suppliers")
        title.setStyleSheet(f"font-size:22px;font-weight:bold;color:{T['primary']};")
        hdr.addWidget(title)
        hdr.addStretch()
        add_btn = QPushButton("＋  Add Supplier")
        add_btn.setStyleSheet(f"background-color:{T['primary']}; color:white; font-weight:bold; padding:0 16px; border-radius:4px;")
        add_btn.setFixedHeight(34)
        add_btn.clicked.connect(self._add)
        
        self.edit_btn = QPushButton("✏️  Edit")
        self.edit_btn.setStyleSheet(f"background-color:{T['secondary']}; color:white; font-weight:bold; padding:0 16px; border-radius:4px;")
        self.edit_btn.setFixedHeight(34)
        self.edit_btn.clicked.connect(self._edit)
        self.edit_btn.setEnabled(False)
        
        self.del_btn = QPushButton("🗑  Delete")
        self.del_btn.setStyleSheet("background-color:#c0392b; color:white; font-weight:bold; padding:0 16px; border-radius:4px;")
        self.del_btn.setFixedHeight(34)
        self.del_btn.clicked.connect(self._delete)
        self.del_btn.setEnabled(False)
        
        hdr.addWidget(add_btn)
        hdr.addWidget(self.edit_btn)
        hdr.addWidget(self.del_btn)
        root.addLayout(hdr)

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Search suppliers…")
        self.search.setObjectName("search_bar")
        self.search.textChanged.connect(self.refresh)
        root.addWidget(self.search)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["#", "Supplier Name", "Address", "Location"])
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
        keyword = self.search.text().strip() if hasattr(self, 'search') else ""
        q = self.session.query(Supplier).order_by(Supplier.supplier_name)
        if keyword:
            q = q.filter(Supplier.supplier_name.ilike(f"%{keyword}%"))
        suppliers = q.all()
        self.table.setRowCount(len(suppliers))
        for i, s in enumerate(suppliers):
            self.table.setItem(i, 0, QTableWidgetItem(str(s.id)))
            self.table.setItem(i, 1, QTableWidgetItem(s.supplier_name or ""))
            self.table.setItem(i, 2, QTableWidgetItem(s.address or ""))
            self.table.setItem(i, 3, QTableWidgetItem(s.location_url or ""))
            for c in range(4):
                if self.table.item(i, c):
                    self.table.item(i, c).setData(Qt.ItemDataRole.UserRole, s.id)

    def _add(self):
        dlg = SupplierDialog(self.session, parent=self)
        if dlg.exec(): self.refresh()

    def _edit(self):
        row = self.table.currentRow()
        if row < 0: return
        sid = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        dlg = SupplierDialog(self.session, sid, parent=self)
        if dlg.exec(): self.refresh()

    def _delete(self):
        row = self.table.currentRow()
        if row < 0: return
        sid = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        name = self.table.item(row, 1).text()
        reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete supplier '{name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                s = self.session.get(Supplier, sid)
                if s:
                    self.session.delete(s)
                    self.session.commit()
                    self.refresh()
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Error", f"Cannot delete supplier because it is in use.\n\nDetails: {str(e)}")


class SupplierDialog(QDialog):
    def __init__(self, session, supplier_id=None, parent=None):
        super().__init__(parent)
        self.session     = session
        self.supplier_id = supplier_id
        self.setWindowTitle("Edit Supplier" if supplier_id else "Add Supplier")
        self.setMinimumWidth(500)
        self._build_ui()
        if supplier_id:
            self._load()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(12)

        tabs = QTabWidget()

        # Tab 1: Info
        info_tab = QWidget()
        form = QFormLayout(info_tab)
        self.name_edit     = QLineEdit()
        self.code_edit     = QLineEdit()
        self.address_edit  = QTextEdit(); self.address_edit.setMaximumHeight(70)
        self.location_edit = QLineEdit()
        self.location_edit.setPlaceholderText("Google Maps URL")
        self.notes_edit    = QTextEdit(); self.notes_edit.setMaximumHeight(70)
        form.addRow("Supplier Name *", self.name_edit)
        form.addRow("Code",            self.code_edit)
        form.addRow("Address",         self.address_edit)
        form.addRow("Location URL",    self.location_edit)
        form.addRow("Notes",           self.notes_edit)
        tabs.addTab(info_tab, "Info")

        # Tab 2: Contacts
        contacts_tab = QWidget()
        c_lay = QVBoxLayout(contacts_tab)
        c_hdr = QHBoxLayout()
        add_contact_btn = QPushButton("＋  Add Contact")
        add_contact_btn.setStyleSheet(f"background-color:{T['secondary']}; color:white; font-weight:bold; padding:6px 12px; border-radius:4px;")
        add_contact_btn.clicked.connect(self._add_contact)
        
        self.edit_con_btn = QPushButton("✏️  Edit")
        self.edit_con_btn.setStyleSheet(f"background-color:{T['secondary']}; color:white; font-weight:bold; padding:6px 12px; border-radius:4px;")
        self.edit_con_btn.clicked.connect(self._edit_contact)
        self.edit_con_btn.setEnabled(False)
        
        self.del_con_btn = QPushButton("🗑  Delete")
        self.del_con_btn.setStyleSheet("background-color:#c0392b; color:white; font-weight:bold; padding:6px 12px; border-radius:4px;")
        self.del_con_btn.clicked.connect(self._delete_contact)
        self.del_con_btn.setEnabled(False)
        
        c_hdr.addStretch()
        c_hdr.addWidget(add_contact_btn)
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
        tabs.addTab(contacts_tab, "Contacts")

        lay.addWidget(tabs)

        btns = QHBoxLayout()
        btns.addStretch()
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
        s = self.session.get(Supplier, self.supplier_id)
        if not s: return
        self.name_edit.setText(s.supplier_name or "")
        self.code_edit.setText(s.supplier_code or "")
        self.address_edit.setPlainText(s.address or "")
        self.location_edit.setText(s.location_url or "")
        self.notes_edit.setPlainText(s.notes or "")
        self._load_contacts()

    def _load_contacts(self):
        contacts = (
            self.session.query(SupplierContact)
            .filter_by(supplier_id=self.supplier_id)
            .all()
        )
        self.contacts_table.setRowCount(len(contacts))
        for i, c in enumerate(contacts):
            proj_name = c.project.project_name if c.project else ""
            for j, val in enumerate([c.name, c.position or "", c.mobile or "", c.email or "", proj_name]):
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, c.id)
                self.contacts_table.setItem(i, j, item)

    def _add_contact(self):
        if not self.supplier_id:
            QMessageBox.information(self, "Save First", "Please save the supplier first.")
            return
        from ui.suppliers.contact_dialog import SupplierContactDialog
        dlg = SupplierContactDialog(self.session, self.supplier_id, parent=self)
        if dlg.exec():
            self._load_contacts()

    def _edit_contact(self):
        row = self.contacts_table.currentRow()
        if row < 0: return
        cid = self.contacts_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        from ui.suppliers.contact_dialog import SupplierContactDialog
        dlg = SupplierContactDialog(self.session, self.supplier_id, contact_id=cid, parent=self)
        if dlg.exec(): self._load_contacts()

    def _delete_contact(self):
        row = self.contacts_table.currentRow()
        if row < 0: return
        cid = self.contacts_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        name = self.contacts_table.item(row, 0).text()
        reply = QMessageBox.question(self, "Confirm Delete", f"Delete contact '{name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            c = self.session.get(SupplierContact, cid)
            if c:
                self.session.delete(c)
                self.session.commit()
                self._load_contacts()

    def _save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Supplier name is required.")
            return
        if self.supplier_id:
            s = self.session.get(Supplier, self.supplier_id)
        else:
            s = Supplier()
            self.session.add(s)
        s.supplier_name = name
        s.supplier_code = self.code_edit.text().strip() or None
        s.address       = self.address_edit.toPlainText().strip() or None
        s.location_url  = self.location_edit.text().strip() or None
        s.notes         = self.notes_edit.toPlainText().strip() or None
        self.session.commit()
        self.supplier_id = s.id
        self.accept()
