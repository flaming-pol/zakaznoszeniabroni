import logging
import requests
import time

from datetime import datetime

from znb.config import get_config
from znb.db import LegalActCRUD, StatsCRUD
from znb.db.session import SessionLocal
from znb.models import SmsNotificationCapability
from znb.crawler import dziennik_ustaw_search_v2
from .enricher import enricher
from .sms_notifications import process_sms_alerts


def parser_wrapper():
    try:
        parser()
    except Exception as e:
        logging.error(f"Podczas parsowania Dziennika wystąpił błąd: {e}")
        # raise
        exit(1)


def parser():
    start_time = time.time()
    config = get_config()
    year = config.PARSER_YEAR
    if config.PARSER_YEAR_CURRENT:
        year = datetime.now().year
    logging.info(f"Uruchomiono parser dla roku {year}")

    db_session = SessionLocal()
    db_acts = LegalActCRUD()
    db_stats = StatsCRUD()
    new_records = 0

    if year != 0:
        db_entries = db_acts.get_by_year(db_session, year)
    else:
        logging.warning("Odpytanie o wszystkie akty prawne generuje dużo zapytań http!")
        db_entries = db_acts.get(db_session)

    acts = dziennik_ustaw_search_v2(year)
    for act in acts:
        db_entry = [i for i in db_entries if
                    (i.number == act.number) and (i.year == act.year)]
        if db_entry:
            logging.debug(f"---> znaleziono w bazie rekord: {act.number}/{act.year} z"
                          f" {act.published_date}, id w bazie: {db_entry[0].id}")
        else:
            # dodanie rozporzadzenia do bazy
            new_record = db_acts.create(db_session,
                                        name=act.name,
                                        number=int(act.number),
                                        year=int(act.year),
                                        published_date=act.published_date,
                                        pdf_url=act.pdf_url,
                                        enriched=False,
                                        sms_capable=SmsNotificationCapability.alert
                                        )
            logging.info(f"===> dodano do bazy rekord: {act.number}/{act.year} z"
                         f" {act.published_date} id w bazie: {new_record.id}")
            new_records += 1
            # dodanie informacji wzbogacających rozporządzenie
            if not new_record.id:
                continue
            is_enriched = enricher(db_session, new_record)
            if is_enriched:
                enriched_act = db_acts.get_by_id(db_session, id=new_record.id)
                for detail in enriched_act.detail:
                    logging.info(f"     obszar: {detail.area}")
                    for t in detail.time:
                        logging.info(f"      {t.begin} - {t.end}")
    if year != 0:
        db_items = db_acts.count_by_year(db_session, year)
    else:
        db_items = db_acts.count(db_session)

    # timestamp aktualizacji danych
    if new_records > 0:
        db_stats.update(db_session, db_update=True)
        # Wysyłka alertów SMS
        if config.SMS_ENABLED:
            process_sms_alerts()
    else:
        db_stats.update(db_session, db_update=False)

    logging.info(f"w Dzienniku znaleziono rekordów: {len(acts)},"
                 f" w bazie znaleziono rekordów: {db_items},"
                 f" dodano do bazy rekordów: {new_records},"
                 f" czas: {time.time()-start_time:.4f} s.")
    if len(acts) < db_items:
        logging.warning(f"Wykryto podejrzaną sytuację: liczba rekordów w DU {len(acts)}"
                        f" jest mniejsza niż w bazie: {db_items}")
    db_session.close()
