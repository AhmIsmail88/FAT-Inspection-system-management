"""
repositories/base_repository.py
Generic CRUD — all other repositories extend this.
"""
from typing import TypeVar, Generic, Type
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: Session):
        self.model   = model
        self.session = session

    def get_by_id(self, record_id: int) -> T | None:
        return self.session.get(self.model, record_id)

    def get_all(self) -> list[T]:
        return self.session.query(self.model).all()

    def add(self, obj: T) -> T:
        self.session.add(obj)
        self.session.flush()
        return obj

    def delete(self, obj: T) -> None:
        self.session.delete(obj)
        self.session.flush()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
