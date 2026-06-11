"""repositories/project_repository.py"""
from sqlalchemy.orm import Session
from models.project import Project
from repositories.base_repository import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, session: Session):
        super().__init__(Project, session)

    def get_active(self) -> list[Project]:
        return self.session.query(Project).filter_by(status="Active").order_by(Project.project_name).all()

    def search(self, keyword: str) -> list[Project]:
        k = f"%{keyword}%"
        return self.session.query(Project).filter(Project.project_name.ilike(k)).all()

    def get_all_ordered(self) -> list[Project]:
        return self.session.query(Project).order_by(Project.project_name).all()
