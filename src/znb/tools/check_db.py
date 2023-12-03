import logging

from sqlalchemy.sql import text
from tenacity import retry, stop_after_attempt, wait_fixed

from znb.db.session import SessionLocal

logger = logging.getLogger()


@retry(
    stop=stop_after_attempt(300),  # 5min
    wait=wait_fixed(1),
)
def check_db():
    logging.warning("Testowanie połączenia z bazą danych...")
    try:
        db = SessionLocal()
        sql = text("SELECT 1")
        db.execute(sql)
    except Exception as e:
        logger.error(e)
        raise e
    finally:
        db.close()
