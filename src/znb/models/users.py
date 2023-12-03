from sqlalchemy import Column, DateTime, String, Boolean
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from znb.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(INTEGER(unsigned=True), primary_key=True)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    email = Column(String(320), unique=False, nullable=False)
    is_active = Column(Boolean, default=False, unique=False, nullable=False)
    confirmation = Column(String(256), unique=False, nullable=True)

    notification = relationship("Notification", back_populates="user",
                                cascade="all, delete")
