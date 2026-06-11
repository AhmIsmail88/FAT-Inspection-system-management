from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database.connection import Base


class Attachment(Base):
    __tablename__ = "attachments"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    fat_record_id   = Column(Integer, ForeignKey("fat_records.id", ondelete="CASCADE"), nullable=False)
    file_name       = Column(String(500), nullable=False)
    file_type       = Column(String(20))    # pdf, docx, xlsx, msg, jpg, png, zip
    file_path       = Column(Text, nullable=False)   # Relative path inside ATTACHMENTS_PATH
    uploaded_by     = Column(Integer, ForeignKey("users.id"))
    uploaded_at     = Column(DateTime, default=func.now())

    uploader        = relationship("User", backref="attachments")

    def __repr__(self):
        return f"<Attachment {self.file_name}>"
