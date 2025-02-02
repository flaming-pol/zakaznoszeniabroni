import logging
import requests
from datetime import datetime
from sqlalchemy.orm import Session

from znb.db import DetailCRUD, DetailTimeCRUD, LegalActCRUD
from znb.db.session import SessionLocal
from znb.models import LegalAct
from znb.pdf import scan_pdf


def enricher(db_session: Session, record: LegalAct) -> bool:
    """
    Wzbogacanie rozporządzenia już istniejącego w bazie.

    Wzbogacanie polega na parsowaniu pliku PDF z rozporządzeniem i wyciągięciu:
    obszaru i dat obowiązywania zakazu.
    """
    if record.year < 2008:
        logging.error("Wzbogacanie rozporządzeń działa tylko dla rozporządzeń od 2008r.")
        return False
    db_acts = LegalActCRUD()
    db_enrichements = DetailCRUD()
    db_enrichements_time = DetailTimeCRUD()
    pdf_details = []
    record_id = record.id
    pdf_url = record.pdf_url
    try:
        pdf_request = requests.get(pdf_url)
        if pdf_request.status_code == 200:
            pdf_details = scan_pdf(stream=pdf_request.content)
        else:
            logging.error(f"Blad przy pobieraniu PDF {pdf_url} "
                          f"-- kod http: {pdf_request.status_code}")
            return False
    except Exception as e:
        logging.warning(f"Bład podczas analizy PDF-a: {e}. Kontynuuje bez wzbogacania!")
        return False

    if not pdf_details:
        return False
    for detail in pdf_details:
        area = detail.get('area')
        dates = detail.get('dates')
        dates_single = dates.get('days')
        dates_ranges = dates.get('ranges')
        detail_record = db_enrichements.create(db_session,
                                               act_id=record_id,
                                               area=area)
        if not detail_record:
            return False
        for d in dates_single:
            begin = datetime.strptime(d, "%d-%m-%Y")
            end = begin.replace(hour=23, minute=59, second=59)
            db_enrichements_time.create(db_session,
                                        detail_id=detail_record.id,
                                        begin=begin,
                                        end=end)
        for d in dates_ranges:
            begin = datetime.strptime(d[0], "%d-%m-%Y")
            end = datetime.strptime(d[1], "%d-%m-%Y")
            end = end.replace(hour=23, minute=59, second=59)
            db_enrichements_time.create(db_session,
                                        detail_id=detail_record.id,
                                        begin=begin,
                                        end=end)
    # aktualizacja metryki rozporzadzenia
    record.enriched = True
    db_acts.update(db_session, record)
    return True


def find_unenriched(year_begin: int = 2008, year_end: int = 0):
    """
    Funkcja służy do poszukiwana niewzbogaconych rozporządzeń i ich wzbogacania.

    Przydatne w sytuacji, gdy coś podczas wzbogacania się nie uda.
    """
    db_session = SessionLocal()
    db_acts = LegalActCRUD()
    if year_begin < 2008:
        year_begin = 2008
    logging.info("Wzbogacanie rozporządzeń w bazie...")
    records = db_acts.get_not_enriched(db_session, year_begin, year_end)
    for r in records:
        logging.info(f"*** (id={r.id}) nr {r.number} z roku {r.year}")
        is_enriched = enricher(db_session, r)
        if is_enriched:
            enriched_act = db_acts.get_by_id(db_session, id=r.id)
            for detail in enriched_act.detail:
                logging.info(f"     obszar: {detail.area}")
                for t in detail.time:
                    logging.info(f"      {t.begin} - {t.end}")
    logging.info("--- koniec wzbogacania.")
    db_session.close()
