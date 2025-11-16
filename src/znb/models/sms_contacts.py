from sqlalchemy import Column, DateTime, String, Boolean
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.sql import func

from znb.db.session import Base


class SmsContact(Base):
    __tablename__ = "sms_contacts"

    id = Column(INTEGER(unsigned=True), primary_key=True)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    phone_number = Column(String(9), unique=True, nullable=False)
    is_active = Column(Boolean, default=False, unique=False, nullable=False)
    comments = Column(String(360), unique=False, nullable=True)
