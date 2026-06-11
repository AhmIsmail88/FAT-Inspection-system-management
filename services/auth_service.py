"""services/auth_service.py"""
from sqlalchemy.orm import Session
from models.user import User
from repositories.user_repository import UserRepository
from config.settings import DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD


class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.repo    = UserRepository(session)

    def login(self, username: str, password: str) -> User | None:
        user = self.repo.get_by_username(username)
        if user and user.is_active and user.check_password(password):
            return user
        return None

    def ensure_default_admin(self):
        """Called on first launch — creates admin if none exists."""
        if not self.repo.get_by_username(DEFAULT_ADMIN_USERNAME):
            admin = User(
                username      = DEFAULT_ADMIN_USERNAME,
                password_hash = User.hash_password(DEFAULT_ADMIN_PASSWORD),
                full_name     = "System Administrator",
                role          = "Admin",
                is_active     = True,
            )
            self.session.add(admin)
            self.session.commit()

    def change_password(self, user_id: int, new_password: str) -> bool:
        user = self.repo.get_by_id(user_id)
        if not user:
            return False
        user.password_hash = User.hash_password(new_password)
        self.session.commit()
        return True
