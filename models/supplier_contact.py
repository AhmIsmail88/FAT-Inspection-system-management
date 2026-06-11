from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base


class SupplierContact(Base):
    """
    A supplier may have different responsible engineers per project.
    e.g. Schneider → Project A: Ahmed, Project B: Mohamed
    """
    __tablename__ = "supplier_contacts"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id     = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)
    project_id      = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"))
    name            = Column(String(200), nullable=False)
    position        = Column(String(100))
    mobile          = Column(String(30))
    email           = Column(String(200))
    whatsapp        = Column(String(30))
    notes           = Column(Text)

    supplier        = relationship("Supplier", backref="contacts")
    project         = relationship("Project", backref="supplier_contacts")

    def __repr__(self):
        return f"<SupplierContact {self.name} @ {self.supplier_id}>"
