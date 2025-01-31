import logging
from datetime import datetime
from sqlalchemy.orm import Session

from znb.models import Detail, DetailTime

from tenacity import retry, stop_after_attempt, wait_fixed


def enrichement_critical_error(retry_state):
    logging.critical("Błąd bazy danych podczas wzbogacania rozporządzenia! "
                     f"Szczegóły błędu: {retry_state}")


class DetailCRUD():
    def get(self, db: Session, id: int) -> Detail:
        return db.query(Detail).filter(Detail.id == id).first()

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_fixed(5),
        reraise=True,
        retry_error_callback=enrichement_critical_error,
    )
    def create(self, db: Session, act_id: int, area: str) -> Detail:
        detail = Detail(
            act_id=act_id,
            area=area
        )
        db.add(detail)
        db.commit()
        db.refresh(detail)
        return detail

    def delete(self, db: Session, id: int):
        detail = self.get(db, id)
        if detail:
            db.delete(detail)
            db.commit()


class DetailTimeCRUD():
    def get(self, db: Session, id: int) -> DetailTime:
        return db.query(DetailTime).filter(DetailTime.id == id).first()

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_fixed(5),
        reraise=True,
        retry_error_callback=enrichement_critical_error,
    )
    def create(self, db: Session, detail_id: int, begin, end) -> DetailTime:
        detailt = DetailTime(
            detail_id=detail_id,
            begin=begin,
            end=end,
        )
        db.add(detailt)
        db.commit()
        db.refresh(detailt)
        return detailt

    def delete(self, db: Session, id: int):
        detailt = self.get(db, id)
        if detailt:
            db.delete(detailt)
            db.commit()
