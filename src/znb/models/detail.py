from sqlalchemy import Boolean, Column, DateTime, String, Integer, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from znb.db.session import Base


class Detail(Base):
    __tablename__ = "details"
    id = Column(INTEGER(unsigned=True), primary_key=True)
    act_id = Column(INTEGER(unsigned=True), ForeignKey('rozporzadzenia.id'))
    area = Column(String(1024), unique=False, nullable=False)

    act = relationship("LegalAct", back_populates="detail")
    time = relationship("DetailTime", back_populates="detail",
                        cascade="all, delete")


class DetailTime(Base):
    __tablename__ = "detail_times"
    id = Column(INTEGER(unsigned=True), primary_key=True)
    detail_id = Column(INTEGER(unsigned=True), ForeignKey('details.id'))
    begin = Column(DateTime(timezone=True), nullable=False)
    end = Column(DateTime(timezone=True), nullable=False)

    detail = relationship("Detail", back_populates="time")
