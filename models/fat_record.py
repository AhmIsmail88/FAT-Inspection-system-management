from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database.connection import Base


class FATRecord(Base):
    """
    Core FAT/Inspection record.
    Links to Project, Supplier, SupplierContact (responsible engineer),
    Consultant, and ConsultantContact — all per-project.
    """
    __tablename__ = "fat_records"

    id                      = Column(Integer, primary_key=True, autoincrement=True)
    serial_no               = Column(Integer)

    # ─── Core Relations ──────────────────────────────────────────────────────
    project_id              = Column(Integer, ForeignKey("projects.id"), nullable=False)
    supplier_id             = Column(Integer, ForeignKey("suppliers.id"), nullable=False)

    # Responsible supplier engineer for this record (project-specific)
    supplier_contact_id     = Column(Integer, ForeignKey("supplier_contacts.id"))

    # Consultant company for this record
    consultant_id           = Column(Integer, ForeignKey("consultants.id"))

    # Responsible consultant engineer for this record (project-specific)
    consultant_contact_id   = Column(Integer, ForeignKey("consultant_contacts.id"))

    # ─── Inspection Info ──────────────────────────────────────────────────────
    inspection_type         = Column(String(30), default="FAT")
    inspection_date         = Column(Date)
    description             = Column(Text)
    quantity                = Column(String(100))

    # ─── Status ───────────────────────────────────────────────────────────────
    status                  = Column(String(50), default="Pending")
    # Pending / Approved / Rejected / Approved with comments

    # ─── References ───────────────────────────────────────────────────────────
    reference_no            = Column(String(200))
    sap_no                  = Column(String(100))
    po_no                   = Column(String(200))

    # ─── Comments ─────────────────────────────────────────────────────────────
    major_comments          = Column(Text)

    # ─── Audit ────────────────────────────────────────────────────────────────
    created_by              = Column(Integer, ForeignKey("users.id"))
    created_at              = Column(DateTime, default=func.now())
    updated_at              = Column(DateTime, default=func.now(), onupdate=func.now())

    # ─── Relationships ────────────────────────────────────────────────────────
    project                 = relationship("Project",           backref="fat_records")
    supplier                = relationship("Supplier",          backref="fat_records")
    supplier_contact        = relationship("SupplierContact",   backref="fat_records")
    consultant              = relationship("Consultant",         backref="fat_records")
    consultant_contact      = relationship("ConsultantContact",  backref="fat_records")
    creator                 = relationship("User",               backref="fat_records")
    attachments             = relationship("Attachment",         backref="fat_record",
                                           cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FATRecord #{self.serial_no} {self.description[:30] if self.description else ''}>"
