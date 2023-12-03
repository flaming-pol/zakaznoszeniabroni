from datetime import datetime
from sqlalchemy.orm import Session
from typing import List

from znb.models import Stats


class StatsCRUD():
    def get(self, db: Session) -> List[Stats]:
        stats = db.query(Stats)
        return stats.all()

    def update(self, db: Session, db_update: bool = False):
        parse_time = datetime.now()
        update_data = {'last_parse_du': parse_time}
        if db_update:
            db_update_time = parse_time
            update_data.update({'last_update_db': parse_time})
        else:
            db_update_time = None

        old_record = self.get(db)
        if old_record:
            db.query(Stats).update(update_data)
        else:
            obj = Stats(last_parse_du=parse_time,
                        last_update_db=db_update_time)
            db.add(obj)
        db.commit()
