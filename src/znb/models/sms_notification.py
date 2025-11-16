from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from znb.db.session import Base


class SmsNotification(Base):
    __tablename__ = "sms_notifications"

    id = Column(INTEGER(unsigned=True), primary_key=True)
    soft_id = Column(String(32), unique=False, nullable=True)
    date_send = Column(DateTime(timezone=True), server_default=func.now())

    act_id = Column(INTEGER(unsigned=True), ForeignKey('rozporzadzenia.id'))

    act = relationship("LegalAct", back_populates="sms_notification")
