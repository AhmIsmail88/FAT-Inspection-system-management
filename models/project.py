"""
models/project.py
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from database.connection import Base


class Project(Base):
    __tablename__ = "projects"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    project_name    = Column(String(200), nullable=False)
    project_code    = Column(String(50), unique=True)
    client_name     = Column(String(200))
    description     = Column(Text)
    status          = Column(String(20), default="Active")   # Active / Archived / Completed
    notes           = Column(Text)
    created_at      = Column(DateTime, default=func.now())
    updated_at      = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Project {self.project_name}>"
