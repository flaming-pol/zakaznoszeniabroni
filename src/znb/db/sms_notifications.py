from sqlalchemy.orm import Session

from znb.models import SmsNotification


class SmsNotificationCRUD:
    def get(self, db: Session, id: int) -> SmsNotification:
        return db.query(SmsNotification).filter(SmsNotification.id == id).first()

    def get_by_act_id(self, db: Session, act_id: int) -> SmsNotification:
        sql = db.query(SmsNotification).filter(SmsNotification.act_id == act_id)
        return sql.all()

    def get_by_soft_id(self, db: Session, soft_id: str) -> SmsNotification:
        sql = db.query(SmsNotification).filter(SmsNotification.soft_id == soft_id)
        return sql.all()

    def create(self, db: Session, soft_id: str, act_id: int) -> SmsNotification:
        notif = SmsNotification(
            soft_id=soft_id,
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
