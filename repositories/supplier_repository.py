"""repositories/supplier_repository.py"""
from sqlalchemy.orm import Session, joinedload
from models.supplier         import Supplier
from models.supplier_contact import SupplierContact
from repositories.base_repository import BaseRepository


class SupplierRepository(BaseRepository[Supplier]):
    def __init__(self, session: Session):
        super().__init__(Supplier, session)

    def get_all_ordered(self) -> list[Supplier]:
        return self.session.query(Supplier).order_by(Supplier.supplier_name).all()

    def search(self, keyword: str) -> list[Supplier]:
        k = f"%{keyword}%"
        return self.session.query(Supplier).filter(Supplier.supplier_name.ilike(k)).all()

    def get_contacts_for_project(self, supplier_id: int, project_id: int) -> list[SupplierContact]:
        return (
            self.session.query(SupplierContact)
            .filter_by(supplier_id=supplier_id, project_id=project_id)
            .all()
        )

    def get_all_contacts(self, supplier_id: int) -> list[SupplierContact]:
        return (
            self.session.query(SupplierContact)
            .options(joinedload(SupplierContact.project))
            .filter_by(supplier_id=supplier_id)
            .all()
        )
