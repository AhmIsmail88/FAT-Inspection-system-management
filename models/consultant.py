from sqlalchemy import Column, Integer, String, Text
from database.connection import Base


class Consultant(Base):
    __tablename__ = "consultants"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    company_name    = Column(String(200), nullable=False)
    notes           = Column(Text)

    def __repr__(self):
        return f"<Consultant {self.company_name}>"
