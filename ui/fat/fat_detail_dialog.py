import webbrowser
import urllib.parse

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTabWidget, QWidget,
    QGridLayout, QScrollArea,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QColor, QCursor, QDesktopServices
from PyQt6.QtCore import QUrl

from config.settings       import THEME as T, STATUS_COLORS
from services.fat_service  import FATService


def _open_link(url: str):
    """Open a URL in the default application."""
    QDesktopServices.openUrl(QUrl(url))


class LinkLabel(QLabel):
    """A QLabel that looks and behaves like a hyperlink."""
    def __init__(self, text: str, url: str, parent=None):
        super().__init__(text, parent)
        self._url = url
        self.setWordWrap(True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.setStyleSheet(
            "color: #1a6fb5; font-size:13px; text-decoration: underline;"
        )
        self.setToolTip(f"Click to open: {url}")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            _open_link(self._url)
        super().mousePressEvent(event)


class FieldRow(QWidget):
    """
    A label+value row. Supports special field types:
      field_type='email'  → clickable mailto: link (opens Outlook)
      field_type='phone'  → clickable WhatsApp link
      field_type='url'    → clickable URL (Google Maps etc.)
      field_type=None     → plain text (default)
    """
    def __init__(self, label: str, value: str, field_type: str = None, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 2, 0, 2)
        lay.setSpacing(10)

        lbl = QLabel(label + ":")
        lbl.setFixedWidth(160)
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        lbl.setStyleSheet(f"color:{T['text_light']}; font-size:12px; font-weight:bold;")

        if value and field_type == "email":
            url = f"mailto:{value}"
            val = LinkLabel(value, url)
        elif value and field_type == "phone":
            # Normalize: remove spaces/dashes, add country code if starts with 0
            phone = value.replace(" ", "").replace("-", "").replace("+", "")
            if phone.startswith("0"):
                phone = "2" + phone   # Egypt country code
            url = f"https://wa.me/{phone}"
            val = LinkLabel(value, url)
        elif value and field_type == "url":
            val = LinkLabel(value, value)
        else:
            val = QLabel(value or "—")
            val.setWordWrap(True)
            val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            val.setStyleSheet(f"color:{T['text']}; font-size:13px;")

        lay.addWidget(lbl)
        lay.addWidget(val, 1)


class FATDetailDialog(QDialog):
    def __init__(self, session, current_user, record_id: int, parent=None):
        super().__init__(parent)
        self.session      = session
        self.current_user = current_user
        self.record_id    = record_id
        self._build_ui()

    def _build_ui(self):
        self.setMinimumWidth(820)
        self.setMinimumHeight(620)
        self.setModal(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        svc = FATService(self.session)
        rec = svc.get_by_id(self.record_id)
        if not rec:
            QLabel("Record not found").setParent(self)
            return

        # ── Header ────────────────────────────────────────────────────────
        header_frame = QFrame()
        header_frame.setStyleSheet(f"background:{T['primary']};")
        h_lay = QHBoxLayout(header_frame)
        h_lay.setContentsMargins(20, 14, 20, 14)

        title_lbl = QLabel(f"FAT Record  #{'%04d' % (rec.serial_no or 0)}")
        title_lbl.setStyleSheet("color:white; font-size:16px; font-weight:bold;")
        h_lay.addWidget(title_lbl)
        h_lay.addStretch()

        # Status badge in header
        color      = STATUS_COLORS.get(rec.status, "#95a5a6")
        text_color = "#333" if rec.status == "Approved with comments" else "white"
        status_lbl = QLabel(rec.status or "")
        status_lbl.setStyleSheet(
            f"background:{color}; color:{text_color}; border-radius:5px;"
            f" padding:4px 14px; font-size:12px; font-weight:bold;"
        )
        h_lay.addWidget(status_lbl)
        root.addWidget(header_frame)

        # ── Tabs ──────────────────────────────────────────────────────────
        tabs = QTabWidget()

        # ── Tab 1: Details ────────────────────────────────────────────────
        details_page = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        body = QWidget()
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(24, 16, 24, 16)
        body_lay.setSpacing(6)

        # Fields: (label, value, field_type)  field_type=None|'email'|'phone'|'url'
        fields = [
            ("Project",             rec.project.project_name if rec.project else "",               None),
            ("Supplier",            rec.supplier.supplier_name if rec.supplier else "",             None),
            ("Supplier Location",   rec.supplier.location_url if rec.supplier and rec.supplier.location_url else "", "url"),
            ("Supplier Engineer",   rec.supplier_contact.name if rec.supplier_contact else "",     None),
            ("Supplier Mobile",     rec.supplier_contact.mobile if rec.supplier_contact else "",   "phone"),
            ("Consultant",          rec.consultant.company_name if rec.consultant else "",          None),
            ("Consultant Engineer", rec.consultant_contact.name if rec.consultant_contact else "", None),
            ("Consultant Mobile",   rec.consultant_contact.mobile if rec.consultant_contact else "", "phone"),
            ("Consultant Email",    rec.consultant_contact.email if rec.consultant_contact else "", "email"),
            ("Inspection Type",     rec.inspection_type or "",                                     None),
            ("Inspection Date",     str(rec.inspection_date) if rec.inspection_date else "",        None),
            ("Description",         rec.description or "",                                          None),
            ("Quantity",            rec.quantity or "",                                             None),
            ("PO Number",           rec.po_no or "",                                               None),
            ("SAP Number",          rec.sap_no or "",                                              None),
            ("Reference No",        rec.reference_no or "",                                        None),
            ("Major Comments",      rec.major_comments or "",                                      None),
            ("Created",             rec.created_at.strftime("%d/%m/%Y %H:%M") if rec.created_at else "", None),
            ("Last Updated",        rec.updated_at.strftime("%d/%m/%Y %H:%M") if rec.updated_at else "", None),
        ]

        for label, value, field_type in fields:
            body_lay.addWidget(FieldRow(label, value, field_type))

        body_lay.addStretch()
        scroll.setWidget(body)
        outer_lay = QVBoxLayout(details_page)
        outer_lay.setContentsMargins(0, 0, 0, 0)
        outer_lay.addWidget(scroll)
        tabs.addTab(details_page, "📋  Details")

        # ── Tab 2: Attachments ────────────────────────────────────────────
        from ui.attachments.attachments_panel import AttachmentsPanel
        att_panel = AttachmentsPanel(self.session, self.current_user, self.record_id)
        tabs.addTab(att_panel, "📎  Attachments")

        root.addWidget(tabs)

        # ── Footer buttons ────────────────────────────────────────────────
        footer = QFrame()
        footer.setStyleSheet(f"background:{T['bg']}; border-top:1px solid {T['border']};")
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(20, 10, 20, 10)
        f_lay.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(38)
        close_btn.setStyleSheet(
            "background:#95a5a6;color:white;border-radius:5px;padding:0 20px;"
        )
        close_btn.clicked.connect(self.reject)

        edit_btn = QPushButton("✏️  Edit Record")
        edit_btn.setFixedHeight(38)
        edit_btn.setStyleSheet(
            f"background:{T['primary']};color:white;border-radius:5px;"
            f"padding:0 24px;font-weight:bold;"
        )
        edit_btn.clicked.connect(self._open_edit)

        f_lay.addWidget(close_btn)
        f_lay.addWidget(edit_btn)
        root.addWidget(footer)

        # Window title
        proj = rec.project.project_name if rec.project else ""
        sup  = rec.supplier.supplier_name if rec.supplier else ""
        self.setWindowTitle(f"FAT #{rec.serial_no}  —  {proj}  /  {sup}")

    def _open_edit(self):
        from ui.fat.fat_form_dialog import FATFormDialog
        dlg = FATFormDialog(self.session, self.current_user, record_id=self.record_id, parent=self)
        if dlg.exec():
            self.accept()   # Close detail view and refresh table
