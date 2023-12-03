from sqlalchemy import Column, DateTime, String, Integer
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from znb.db.session import Base


class LegalAct(Base):
    __tablename__ = "rozporzadzenia"

    id = Column(INTEGER(unsigned=True), primary_key=True)
    name = Column(String(512), unique=False, nullable=False)
    number = Column(Integer, unique=False, nullable=True)
    year = Column(Integer, unique=False, nullable=True)
    published_date = Column(String(16), unique=False, nullable=True)
    pdf_url = Column(String(255), unique=False, nullable=True)
    date_created = Column(DateTime(timezone=True), server_default=func.now())

    # notifications
    notif_started_proc = Column(DateTime(timezone=True), unique=False, nullable=True)
    notif_finished_proc = Column(DateTime(timezone=True), unique=False, nullable=True)

    notification = relationship("Notification", back_populates="act",
                                cascade="all, delete")
