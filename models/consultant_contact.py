from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base


class ConsultantContact(Base):
    """Consultant engineer assigned to a specific project."""
    __tablename__ = "consultant_contacts"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    consultant_id   = Column(Integer, ForeignKey("consultants.id", ondelete="CASCADE"), nullable=False)
    project_id      = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"))
    name            = Column(String(200), nullable=False)
    position        = Column(String(100))
    mobile          = Column(String(30))
    email           = Column(String(200))
    notes           = Column(Text)

    consultant      = relationship("Consultant", backref="contacts")
    project         = relationship("Project", backref="consultant_contacts")

    def __repr__(self):
        return f"<ConsultantContact {self.name}>"
