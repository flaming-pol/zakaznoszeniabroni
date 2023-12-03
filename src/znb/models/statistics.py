from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func

from znb.db.session import Base


class Stats(Base):
    __tablename__ = "statystyki"

    last_parse_du = Column(DateTime(timezone=True), primary_key=True,
                           server_default=func.now())
    last_update_db = Column(DateTime(timezone=True), nullable=True)
