from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from znb.db.session import Base


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(INTEGER(unsigned=True), primary_key=True)
    date_send = Column(DateTime(timezone=True), server_default=func.now())

    user_id = Column(INTEGER(unsigned=True), ForeignKey('users.id'))
    act_id = Column(INTEGER(unsigned=True), ForeignKey('rozporzadzenia.id'))

    user = relationship("User", back_populates="notification")
    act = relationship("LegalAct", back_populates="notification")
