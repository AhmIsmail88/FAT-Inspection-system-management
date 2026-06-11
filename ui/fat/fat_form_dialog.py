"""ui/fat/fat_form_dialog.py — Add / Edit FAT Record (with Attachments tab)"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QComboBox, QDateEdit,
    QPushButton, QGroupBox, QScrollArea,
    QWidget, QFrame, QTabWidget,
)
from PyQt6.QtCore import Qt, QDate

from config.settings  import THEME as T, FAT_STATUSES, INSPECTION_TYPES
from services.fat_service import FATService
from repositories.project_repository    import ProjectRepository
from repositories.supplier_repository   import SupplierRepository
from models.consultant         import Consultant
from models.consultant_contact import ConsultantContact


class FATFormDialog(QDialog):
    def __init__(self, session, current_user, record_id=None, parent=None):
        super().__init__(parent)
        self.session      = session
        self.current_user = current_user
        self.record_id    = record_id
        self.is_edit      = record_id is not None
        self._attachments_panel = None
        self._build_ui()
        if self.is_edit:
            self._load_record()

    # ─────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        title_text = "Edit FAT Record" if self.is_edit else "Add FAT Record"
        self.setWindowTitle(title_text)
        self.setMinimumWidth(780)
        self.setMinimumHeight(660)
        self.setModal(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar ────────────────────────────────────────────────────
        header = QLabel(title_text)
        header.setStyleSheet(
            f"background:{T['primary']}; color:white; font-size:15px;"
            f" font-weight:bold; padding:14px 20px;"
        )
        root.addWidget(header)

        # ── Tab widget ────────────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab { padding: 9px 22px; font-size: 13px; }
        """)

        # Tab 1 — Details
        self.tabs.addTab(self._build_details_tab(), "📋  Details")

        # Tab 2 — Attachments  (lazy: created after first save if new record)
        self._att_tab_placeholder = QWidget()
        att_ph_lay = QVBoxLayout(self._att_tab_placeholder)
        self._att_placeholder_lbl = QLabel(
            "💾  Save the record first, then you can add attachments."
        )
        self._att_placeholder_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._att_placeholder_lbl.setStyleSheet(
            f"color:{T['text_light']}; font-size:13px; padding:40px;"
        )
        att_ph_lay.addWidget(self._att_placeholder_lbl)
        self.tabs.addTab(self._att_tab_placeholder, "📎  Attachments")

        root.addWidget(self.tabs)

        # ── Footer buttons ────────────────────────────────────────────────
        footer = QFrame()
        footer.setStyleSheet(f"background:{T['bg']}; border-top:1px solid {T['border']};")
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(20, 10, 20, 10)
        f_lay.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(38)
        cancel_btn.setStyleSheet(
            "background:#95a5a6;color:white;border-radius:5px;padding:0 20px;"
        )
        cancel_btn.clicked.connect(self.reject)

        self.save_btn = QPushButton("Save Record")
        self.save_btn.setFixedHeight(38)
        self.save_btn.setStyleSheet(
            f"background:{T['primary']};color:white;border-radius:5px;"
            f"padding:0 24px;font-weight:bold;"
        )
        self.save_btn.clicked.connect(self._save)

        f_lay.addWidget(cancel_btn)
        f_lay.addWidget(self.save_btn)
        root.addWidget(footer)

        # Populate dropdowns
        self._populate_dropdowns()

        # If editing, load attachments tab immediately
        if self.is_edit:
            self._load_attachments_tab(self.record_id)

    # ─── Details tab ──────────────────────────────────────────────────────
    def _build_details_tab(self):
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        body = QWidget()
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(20, 16, 20, 16)
        body_lay.setSpacing(14)

        # Group 1 — Project & Supplier
        grp1 = QGroupBox("Project & Supplier")
        form1 = QFormLayout(grp1)
        form1.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form1.setSpacing(10)

        self.project_cb = QComboBox()
        self.project_cb.currentIndexChanged.connect(self._on_project_changed)
        form1.addRow("Project *", self.project_cb)

        self.supplier_cb = QComboBox()
        self.supplier_cb.currentIndexChanged.connect(self._on_supplier_changed)
        form1.addRow("Supplier *", self.supplier_cb)

        self.sup_contact_cb = QComboBox()
        form1.addRow("Supplier Engineer", self.sup_contact_cb)
        body_lay.addWidget(grp1)

        # Group 2 — Consultant
        grp2 = QGroupBox("Consultant")
        form2 = QFormLayout(grp2)
        form2.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form2.setSpacing(10)

        self.consultant_cb = QComboBox()
        self.consultant_cb.currentIndexChanged.connect(self._on_consultant_changed)
        form2.addRow("Consultant", self.consultant_cb)

        self.con_contact_cb = QComboBox()
        form2.addRow("Consultant Engineer", self.con_contact_cb)
        body_lay.addWidget(grp2)

        # Group 3 — Inspection Details
        grp3 = QGroupBox("Inspection Details")
        form3 = QFormLayout(grp3)
        form3.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form3.setSpacing(10)

        self.type_cb = QComboBox()
        self.type_cb.addItems(INSPECTION_TYPES)
        form3.addRow("Type", self.type_cb)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        form3.addRow("Date", self.date_edit)

        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(80)
        self.desc_edit.setPlaceholderText("Equipment / material description…")
        form3.addRow("Description", self.desc_edit)

        self.qty_edit = QLineEdit()
        self.qty_edit.setPlaceholderText("e.g.  3 panels")
        form3.addRow("Quantity", self.qty_edit)
        body_lay.addWidget(grp3)

        # Group 4 — Status & References
        grp4 = QGroupBox("Status & References")
        form4 = QFormLayout(grp4)
        form4.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form4.setSpacing(10)

        self.status_cb = QComboBox()
        self.status_cb.addItems(FAT_STATUSES)
        form4.addRow("Status", self.status_cb)

        self.ref_edit = QLineEdit()
        form4.addRow("Reference No", self.ref_edit)

        self.sap_edit = QLineEdit()
        form4.addRow("SAP No", self.sap_edit)

        self.po_edit = QLineEdit()
        form4.addRow("PO No", self.po_edit)

        self.comments_edit = QTextEdit()
        self.comments_edit.setMaximumHeight(80)
        self.comments_edit.setPlaceholderText("Major inspection comments…")
        form4.addRow("Major Comments", self.comments_edit)
        body_lay.addWidget(grp4)

        scroll.setWidget(body)
        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
        return page

    # ─── Attachments tab ──────────────────────────────────────────────────
    def _load_attachments_tab(self, record_id):
        from ui.attachments.attachments_panel import AttachmentsPanel
        panel = AttachmentsPanel(self.session, self.current_user, record_id)
        self._attachments_panel = panel
        # Replace placeholder tab
        idx = self.tabs.indexOf(self._att_tab_placeholder)
        self.tabs.removeTab(idx)
        self.tabs.insertTab(idx, panel, "📎  Attachments")

    # ─── Dropdowns ────────────────────────────────────────────────────────
    def _populate_dropdowns(self):
        proj_repo = ProjectRepository(self.session)
        sup_repo  = SupplierRepository(self.session)

        self.project_cb.addItem("— Select Project —", None)
        for p in proj_repo.get_all_ordered():
            self.project_cb.addItem(p.project_name, p.id)

        self.supplier_cb.addItem("— Select Supplier —", None)
        for s in sup_repo.get_all_ordered():
            self.supplier_cb.addItem(s.supplier_name, s.id)

        self.consultant_cb.addItem("— None —", None)
        for c in self.session.query(Consultant).order_by(Consultant.company_name).all():
            self.consultant_cb.addItem(c.company_name, c.id)

    def _on_project_changed(self):
        self._refresh_supplier_contacts()
        self._refresh_consultant_contacts()

    def _on_supplier_changed(self):
        self._refresh_supplier_contacts()

    def _on_consultant_changed(self):
        self._refresh_consultant_contacts()

    def _refresh_supplier_contacts(self):
        from models.supplier_contact import SupplierContact
        self.sup_contact_cb.clear()
        self.sup_contact_cb.addItem("— Select Engineer —", None)
        sup_id  = self.supplier_cb.currentData()
        proj_id = self.project_cb.currentData()
        if not sup_id:
            return
        contacts = (
            self.session.query(SupplierContact)
            .filter_by(supplier_id=sup_id, project_id=proj_id)
            .all()
        )
        for c in contacts:
            self.sup_contact_cb.addItem(f"{c.name}  {('📱 ' + c.mobile) if c.mobile else ''}", c.id)

    def _refresh_consultant_contacts(self):
        self.con_contact_cb.clear()
        self.con_contact_cb.addItem("— Select Engineer —", None)
        con_id  = self.consultant_cb.currentData()
        proj_id = self.project_cb.currentData()
        if not con_id:
            return
        contacts = (
            self.session.query(ConsultantContact)
            .filter_by(consultant_id=con_id, project_id=proj_id)
            .all()
        )
        for c in contacts:
            self.con_contact_cb.addItem(c.name, c.id)

    # ─── Load for editing ─────────────────────────────────────────────────
    def _load_record(self):
        svc = FATService(self.session)
        rec = svc.get_by_id(self.record_id)
        if not rec:
            return

        self._set_combo(self.project_cb,    rec.project_id)
        self._set_combo(self.supplier_cb,   rec.supplier_id)
        self._refresh_supplier_contacts()
        self._set_combo(self.sup_contact_cb, rec.supplier_contact_id)
        self._set_combo(self.consultant_cb,  rec.consultant_id)
        self._refresh_consultant_contacts()
        self._set_combo(self.con_contact_cb, rec.consultant_contact_id)

        self.type_cb.setCurrentText(rec.inspection_type or "FAT")

        if rec.inspection_date:
            d = rec.inspection_date
            self.date_edit.setDate(QDate(d.year, d.month, d.day))

        self.desc_edit.setPlainText(rec.description or "")
        self.qty_edit.setText(rec.quantity or "")
        self.status_cb.setCurrentText(rec.status or "Pending")
        self.ref_edit.setText(rec.reference_no or "")
        self.sap_edit.setText(rec.sap_no or "")
        self.po_edit.setText(rec.po_no or "")
        self.comments_edit.setPlainText(rec.major_comments or "")

    def _set_combo(self, combo, value):
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                return

    # ─── Save ─────────────────────────────────────────────────────────────
    def _save(self):
        from PyQt6.QtWidgets import QMessageBox

        project_id  = self.project_cb.currentData()
        supplier_id = self.supplier_cb.currentData()

        if not project_id:
            QMessageBox.warning(self, "Validation", "Please select a Project.")
            return
        if not supplier_id:
            QMessageBox.warning(self, "Validation", "Please select a Supplier.")
            return

        d = self.date_edit.date()
        import datetime
        insp_date = datetime.date(d.year(), d.month(), d.day())

        fields = dict(
            project_id            = project_id,
            supplier_id           = supplier_id,
            supplier_contact_id   = self.sup_contact_cb.currentData(),
            consultant_id         = self.consultant_cb.currentData(),
            consultant_contact_id = self.con_contact_cb.currentData(),
            inspection_type       = self.type_cb.currentText(),
            inspection_date       = insp_date,
            description           = self.desc_edit.toPlainText().strip() or None,
            quantity              = self.qty_edit.text().strip() or None,
            status                = self.status_cb.currentText(),
            reference_no          = self.ref_edit.text().strip() or None,
            sap_no                = self.sap_edit.text().strip() or None,
            po_no                 = self.po_edit.text().strip() or None,
            major_comments        = self.comments_edit.toPlainText().strip() or None,
        )

        svc = FATService(self.session, self.current_user.id)
        try:
            if self.is_edit:
                svc.update(self.record_id, **fields)
            else:
                rec = svc.create(**fields)
                self.record_id = rec.id
                self.is_edit   = True
                # Unlock attachments tab
                self._load_attachments_tab(self.record_id)
                self.save_btn.setText("Save Changes")
                QMessageBox.information(
                    self, "Saved",
                    "Record saved! You can now add attachments in the Attachments tab."
                )
                self.tabs.setCurrentIndex(1)
                return
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
