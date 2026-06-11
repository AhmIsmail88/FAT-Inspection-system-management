"""
repositories/fat_repository.py
Search, filter, and CRUD for FAT Records.
"""
from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_

from models.fat_record import FATRecord
from models.project    import Project
from models.supplier   import Supplier
from models.consultant import Consultant
from repositories.base_repository import BaseRepository


class FATRepository(BaseRepository[FATRecord]):
    def __init__(self, session: Session):
        super().__init__(FATRecord, session)

    def _base_query(self):
        """Always eager-load the most-used relations."""
        return (
            self.session.query(FATRecord)
            .options(
                joinedload(FATRecord.project),
                joinedload(FATRecord.supplier),
                joinedload(FATRecord.supplier_contact),
                joinedload(FATRecord.consultant),
                joinedload(FATRecord.consultant_contact),
                joinedload(FATRecord.creator),
            )
        )

    # ── Basic ──────────────────────────────────────────────────────────────
    def get_all(self) -> list[FATRecord]:
        return self._base_query().order_by(FATRecord.serial_no).all()

    def get_by_id(self, record_id: int) -> FATRecord | None:
        return self._base_query().filter(FATRecord.id == record_id).first()

    # ── Global search ──────────────────────────────────────────────────────
    def search(self, keyword: str) -> list[FATRecord]:
        """Search across project, supplier, description, PO, SAP, comments."""
        k = f"%{keyword}%"
        return (
            self._base_query()
            .join(Project,  FATRecord.project_id  == Project.id)
            .join(Supplier, FATRecord.supplier_id == Supplier.id)
            .filter(
                or_(
                    Project.project_name.ilike(k),
                    Supplier.supplier_name.ilike(k),
                    FATRecord.description.ilike(k),
                    FATRecord.po_no.ilike(k),
                    FATRecord.sap_no.ilike(k),
                    FATRecord.reference_no.ilike(k),
                    FATRecord.major_comments.ilike(k),
                    FATRecord.status.ilike(k),
                )
            )
            .order_by(FATRecord.serial_no)
            .all()
        )

    # ── Combined filter ────────────────────────────────────────────────────
    def filter(
        self,
        project_id:    int | None  = None,
        supplier_id:   int | None  = None,
        consultant_id: int | None  = None,
        status:        str | None  = None,
        date_from:     date | None = None,
        date_to:       date | None = None,
    ) -> list[FATRecord]:
        q = self._base_query()
        conditions = []
        if project_id:
            conditions.append(FATRecord.project_id == project_id)
        if supplier_id:
            conditions.append(FATRecord.supplier_id == supplier_id)
        if consultant_id:
            conditions.append(FATRecord.consultant_id == consultant_id)
        if status:
            conditions.append(FATRecord.status == status)
        if date_from:
            conditions.append(FATRecord.inspection_date >= date_from)
        if date_to:
            conditions.append(FATRecord.inspection_date <= date_to)
        if conditions:
            q = q.filter(and_(*conditions))
        return q.order_by(FATRecord.serial_no).all()

    # ── Stats for Dashboard ────────────────────────────────────────────────
    def get_status_counts(self) -> dict[str, int]:
        rows = (
            self.session.query(FATRecord.status, FATRecord.id)
            .all()
        )
        counts = {}
        for status, _ in rows:
            counts[status] = counts.get(status, 0) + 1
        return counts

    def get_monthly_counts(self) -> list[dict]:
        """Returns list of {month, year, count} for trend chart."""
        from sqlalchemy import func, extract
        rows = (
            self.session.query(
                extract("year",  FATRecord.inspection_date).label("year"),
                extract("month", FATRecord.inspection_date).label("month"),
                func.count(FATRecord.id).label("count"),
            )
            .filter(FATRecord.inspection_date.isnot(None))
            .group_by("year", "month")
            .order_by("year", "month")
            .all()
        )
        return [{"year": int(r.year), "month": int(r.month), "count": r.count} for r in rows]

    def get_by_supplier_counts(self) -> list[dict]:
        from sqlalchemy import func
        rows = (
            self.session.query(Supplier.supplier_name, func.count(FATRecord.id).label("count"))
            .join(Supplier, FATRecord.supplier_id == Supplier.id)
            .group_by(Supplier.supplier_name)
            .order_by(func.count(FATRecord.id).desc())
            .all()
        )
        return [{"name": r.supplier_name, "count": r.count} for r in rows]

    def get_next_serial(self) -> int:
        from sqlalchemy import func
        max_serial = self.session.query(func.max(FATRecord.serial_no)).scalar()
        return (max_serial or 0) + 1
