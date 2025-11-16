from sqlalchemy.orm import Session

from znb.models import SmsContact


class SmsContactCRUD:
    # def get(self, db: Session, id: int) -> SmsContact:
    #     return db.query(SmsContact).filter(SmsContact.id == id).first()
    def get(self, db: Session, phone_number: str) -> SmsContact:
        return db.query(SmsContact).filter(SmsContact.phone_number == phone_number).first()

    def get_all(self, db: Session, only_active: bool = False) -> list[SmsContact]:
        if only_active:
            sql = db.query(SmsContact).filter_by(is_active=True)
        else:
            sql = db.query(SmsContact)
        return sql.all()

    def get_by_phone(self, db: Session, phone_number: str) -> SmsContact:
        return db.query(SmsContact).filter(SmsContact.phone_number == phone_number).first()

    def create(self, db: Session, phone_number: str,
               is_active: bool, comments: str) -> SmsContact:
        contact = SmsContact(
            phone_number=phone_number,
            is_active=is_active,
            comments=comments,
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact

    def delete(self, db: Session, phone_number: str):
        contact = db.query(SmsContact).filter(SmsContact.phone_number == phone_number).first()
        if contact:
            db.delete(contact)
            db.commit()

    def count(self, db: Session):
        sql = db.query(SmsContact)
        return sql.count()

    def count_active(self, db: Session):
        sql = db.query(SmsContact).filter_by(is_active=True)
        return sql.count()

    def update(self, db: Session, contact: SmsContact) -> SmsContact:
        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact
