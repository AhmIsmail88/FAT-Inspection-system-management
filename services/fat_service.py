"""
services/fat_service.py
All business logic for FAT Records.
UI never touches the DB directly — always goes through here.
"""
import json
from datetime import date
from sqlalchemy.orm import Session

from models.fat_record   import FATRecord
from models.audit_log    import AuditLog
from repositories.fat_repository import FATRepository


class FATService:
    def __init__(self, session: Session, current_user_id: int | None = None):
        self.session         = session
        self.repo            = FATRepository(session)
        self.current_user_id = current_user_id

    # ── Read ──────────────────────────────────────────────────────────────
    def get_all(self)            -> list[FATRecord]: return self.repo.get_all()
    def get_by_id(self, rid)     -> FATRecord | None: return self.repo.get_by_id(rid)
    def search(self, keyword)    -> list[FATRecord]: return self.repo.search(keyword)
    def get_status_counts(self)  -> dict: return self.repo.get_status_counts()
    def get_monthly_counts(self) -> list: return self.repo.get_monthly_counts()
    def get_supplier_counts(self)-> list: return self.repo.get_by_supplier_counts()

    def filter(self, **kwargs)   -> list[FATRecord]:
        return self.repo.filter(**kwargs)

    # ── Create ────────────────────────────────────────────────────────────
    def create(
        self,
        project_id:             int,
        supplier_id:            int,
        supplier_contact_id:    int | None  = None,
        consultant_id:          int | None  = None,
        consultant_contact_id:  int | None  = None,
        inspection_type:        str         = "FAT",
        inspection_date:        date | None = None,
        description:            str | None  = None,
        quantity:               str | None  = None,
        status:                 str         = "Pending",
        reference_no:           str | None  = None,
        sap_no:                 str | None  = None,
        po_no:                  str | None  = None,
        major_comments:         str | None  = None,
    ) -> FATRecord:
        record = FATRecord(
            serial_no             = self.repo.get_next_serial(),
            project_id            = project_id,
            supplier_id           = supplier_id,
            supplier_contact_id   = supplier_contact_id,
            consultant_id         = consultant_id,
            consultant_contact_id = consultant_contact_id,
            inspection_type       = inspection_type,
            inspection_date       = inspection_date,
            description           = description,
            quantity              = quantity,
            status                = status,
            reference_no          = reference_no,
            sap_no                = sap_no,
            po_no                 = po_no,
            major_comments        = major_comments,
            created_by            = self.current_user_id,
        )
        self.repo.add(record)
        self._audit("CREATE", record.id, None, self._to_dict(record))
        self.session.commit()
        return record

    # ── Update ────────────────────────────────────────────────────────────
    def update(self, record_id: int, **fields) -> FATRecord:
        record   = self.repo.get_by_id(record_id)
        if not record:
            raise ValueError(f"FAT Record #{record_id} not found")
        old_data = self._to_dict(record)

        for key, value in fields.items():
            if hasattr(record, key):
                setattr(record, key, value)

        self._audit("UPDATE", record_id, old_data, self._to_dict(record))
        self.session.commit()
        return record

    # ── Delete ────────────────────────────────────────────────────────────
    def delete(self, record_id: int) -> None:
        record = self.repo.get_by_id(record_id)
        if not record:
            raise ValueError(f"FAT Record #{record_id} not found")
        old_data = self._to_dict(record)
        self.repo.delete(record)
        self._audit("DELETE", record_id, old_data, None)
        self.session.commit()

    # ── Duplicate ─────────────────────────────────────────────────────────
    def duplicate(self, record_id: int) -> FATRecord:
        src = self.repo.get_by_id(record_id)
        if not src:
            raise ValueError(f"FAT Record #{record_id} not found")
        return self.create(
            project_id            = src.project_id,
            supplier_id           = src.supplier_id,
            supplier_contact_id   = src.supplier_contact_id,
            consultant_id         = src.consultant_id,
            consultant_contact_id = src.consultant_contact_id,
            inspection_type       = src.inspection_type,
            description           = src.description,
            quantity              = src.quantity,
            status                = "Pending",
            reference_no          = src.reference_no,
            sap_no                = src.sap_no,
            po_no                 = src.po_no,
        )

    # ── Helpers ───────────────────────────────────────────────────────────
    def _to_dict(self, r: FATRecord) -> dict:
        return {
            "id": r.id, "serial_no": r.serial_no,
            "project_id": r.project_id, "supplier_id": r.supplier_id,
            "status": r.status, "description": r.description,
            "inspection_date": str(r.inspection_date),
            "po_no": r.po_no, "sap_no": r.sap_no,
        }

    def _audit(self, action: str, record_id: int, old: dict | None, new: dict | None):
        log = AuditLog(
            user_id    = self.current_user_id,
            action     = action,
            table_name = "fat_records",
            record_id  = record_id,
            old_value  = json.dumps(old) if old else None,
            new_value  = json.dumps(new) if new else None,
        )
        self.session.add(log)
