from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from database.connection import Base
from sqlalchemy.orm import relationship


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("users.id"))
    action      = Column(String(20))      # CREATE / UPDATE / DELETE
    table_name  = Column(String(100))
    record_id   = Column(Integer)
    old_value   = Column(Text)            # JSON string
    new_value   = Column(Text)            # JSON string
    created_at  = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", backref="audit_logs")
