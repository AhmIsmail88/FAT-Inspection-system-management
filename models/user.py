from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from database.connection import Base
import bcrypt


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    username        = Column(String(100), unique=True, nullable=False)
    password_hash   = Column(String(200), nullable=False)
    full_name       = Column(String(200))
    role            = Column(String(20), default="Engineer")   # Admin / Engineer
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=func.now())

    # ─── Password helpers ────────────────────────────────────────────────────
    @staticmethod
    def hash_password(plain: str) -> str:
        return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

    def check_password(self, plain: str) -> bool:
        return bcrypt.checkpw(plain.encode(), self.password_hash.encode())

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
