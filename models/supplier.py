from sqlalchemy import Column, Integer, String, Text
from database.connection import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    supplier_name   = Column(String(200), nullable=False)
    supplier_code   = Column(String(50), unique=True)
    address         = Column(Text)
    location_url    = Column(Text)   # Google Maps link
    notes           = Column(Text)

    def __repr__(self):
        return f"<Supplier {self.supplier_name}>"
