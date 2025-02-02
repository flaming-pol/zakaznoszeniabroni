from typing import Any, List
from sqlalchemy import and_
from sqlalchemy.orm import Session

from znb.models import LegalAct


class LegalActCRUD():
    def get(self, db: Session) -> LegalAct:
        sql = db.query(LegalAct)
        return sql.all()

    def count(self, db: Session) -> int:
        sql = db.query(LegalAct)
        return sql.count()

    def get_by_id(self, db: Session, id: Any) -> LegalAct:
        return db.query(LegalAct).filter(LegalAct.id == id).first()

    def get_by_year(self, db: Session, year: int) -> List[LegalAct]:
        sql = db.query(LegalAct).filter(LegalAct.year == year)
        return sql.all()

    def get_notif_unfinished(self, db: Session) -> List[LegalAct]:
        sql = db.query(LegalAct).filter(LegalAct.notif_started_proc != None).filter(
            LegalAct.notif_finished_proc == None)
        return sql.all()

    def get_notif_not_started(self, db: Session) -> List[LegalAct]:
        sql = db.query(LegalAct).filter(
            LegalAct.notif_started_proc == None)
        return sql.all()

    def count_by_year(self, db: Session, year: int) -> int:
        sql = db.query(LegalAct).filter(LegalAct.year == year)
        return sql.count()

    def get_by_number(self, db: Session, number: int) -> List[LegalAct]:
        sql = db.query(LegalAct).filter(LegalAct.number == number)
        return sql.all()

    def get_not_enriched(self, db: Session, year_begin: int = 0, year_end: int = 0
                         ) -> List[LegalAct]:
        if (not year_begin) and year_end:
            return []
        elif not year_begin and not year_end:
            sql = db.query(LegalAct).filter(LegalAct.enriched == False)
        elif year_begin and not year_end:
            sql = db.query(LegalAct).filter(and_(LegalAct.enriched == False,
                                                 LegalAct.year >= year_begin))
        else:
            sql = db.query(LegalAct).filter(and_(LegalAct.enriched == False,
                                                 LegalAct.year >= year_begin,
                                                 LegalAct.year <= year_end))
        return sql.all()

    def create(self, db: Session, name: str, number: int, year: int,
               published_date: str, pdf_url: str, enriched: bool = False) -> LegalAct:
        new_legal_act = LegalAct(
            name=name,
            number=number,
            year=year,
            published_date=published_date,
            pdf_url=pdf_url,
            enriched=enriched
        )
        db.add(new_legal_act)
        db.commit()
        db.refresh(new_legal_act)
        return new_legal_act

    def update(self, db: Session, act: LegalAct) -> LegalAct:
        db.add(act)
        db.commit()
        db.refresh(act)
        return act
