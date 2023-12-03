import logging
from sqlalchemy.orm import Session

from znb.models import Notification

from tenacity import retry, stop_after_attempt, wait_fixed


def notification_critical_error(retry_state):
    logging.critical("Błąd podczas dodawania notyfikacji do bazy. Mail został wysłany! "
                     f"Szczegóły błędu: {retry_state}")
    # exit(0)


class NotificationCRUD():
    def get(self, db: Session, id: int) -> Notification:
        return db.query(Notification).filter(Notification.notification_id == id).first()

    @retry(
        stop=stop_after_attempt(240),  # 1 godzina
        wait=wait_fixed(15),
        reraise=True,
        retry_error_callback=notification_critical_error,
    )
    def create(self, db: Session, user_id: int, act_id: int) -> Notification:
        notif = Notification(
            user_id=user_id,
            act_id=act_id,
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif

    def delete(self, db: Session, id: int):
        notif = self.get(db, id)
        if notif:
            db.delete(notif)
            db.commit()
