"""repositories/user_repository.py"""
from sqlalchemy.orm import Session
from models.user import User
from repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session):
        super().__init__(User, session)

    def get_by_username(self, username: str) -> User | None:
        return self.session.query(User).filter_by(username=username).first()

    def get_active_users(self) -> list[User]:
        return self.session.query(User).filter_by(is_active=True).all()
