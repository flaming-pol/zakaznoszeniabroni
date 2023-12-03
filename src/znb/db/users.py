import random
import string

from datetime import datetime, timedelta
from typing import List

from sqlalchemy import not_
from sqlalchemy.orm import Session, contains_eager

from znb.models import Notification, User


class UserCRUD():
    def get(self, db: Session, id: int) -> User:
        return db.query(User).filter(User.id == id).first()

    def get_by_confirmation_string(self, db: Session, confirmation: str) -> User:
        return db.query(User).filter(User.confirmation == confirmation).first()

    def get_users_withou_confirmation_string(self, db: Session) -> List[User]:
        sql = db.query(User).filter_by(is_active=False).filter_by(confirmation=None)
        return sql.all()

    def get_users_never_notified(self, db: Session) -> List[User]:
        sql = db.query(User).filter_by(is_active=True).filter(User.notification == None)
        return sql.all()

    def get_users_not_notified(self, db: Session, act_id: int,) -> List[User]:
        # options(contains_eager(ModelUser.notification)
        sql = db.query(User).filter_by(is_active=True).join(Notification).filter(
            not_(User.notification.any(Notification.act_id == act_id)))
        return sql.all()

    def get_users_to_notify(self, db: Session, act_id: int,) -> List[User]:
        u1 = self.get_users_never_notified(db)
        u2 = self.get_users_not_notified(db, act_id)
        return u1 + u2

    def create(self, db: Session, email: str, is_active: bool = False) -> User:
        while True:
            confirmation_string = ''.join(random.choice(
                string.ascii_letters + string.digits) for i in range(256))
            u = self.get_by_confirmation_string(db, confirmation_string)
            if not u:
                break
        user = User(
            email=email,
            is_active=is_active,
            confirmation=confirmation_string,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def delete(self, db: Session, email: str):
        user = db.query(User).filter(User.email == email).first()
        if user:
            db.delete(user)
            db.commit()

    def delete_not_active(self, db: Session, hours: int = 12) -> List[User]:
        sql = db.query(User).filter(User.is_active == False).filter(
            User.date_created < datetime.now() - timedelta(hours=hours))
        users = sql.all()
        for u in users:
            db.delete(u)
            db.commit()
        return users

    def count(self, db: Session):
        sql = db.query(User)
        return sql.count()

    def count_active(self, db: Session):
        sql = db.query(User).filter_by(is_active=True)
        return sql.count()

    def update(self, db: Session, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
