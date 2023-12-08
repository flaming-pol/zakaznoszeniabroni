import random
import string
import time
import logging

from datetime import datetime

from znb.config import get_config
from znb.db import NotificationCRUD, UserCRUD, LegalActCRUD
from znb.db.session import SessionLocal
from znb.mailing import (
    SmtpWrapper,
    notification_mail_render,
    confirmation_mail_render,
)
from znb.models import LegalAct


def delete_users_not_activated():
    db = SessionLocal()
    db_users = UserCRUD()
    users = db_users.delete_not_active(db, hours=24)
    db.close()
    for u in users:
        logging.warning(f"Usunieto użytkownika: id={u.id}, email={u.email}"
                        " - brak aktywacji")


def process_send_confirmation():
    config = get_config()
    db = SessionLocal()
    db_users = UserCRUD()
    users = db_users.get_users_withou_confirmation_string(db)
    if users:
        logging.debug("Wysyłanie e-mail z potiwerdzeniem założenia konta")
        s = SmtpWrapper(config.MAIL_SERVER, config.MAIL_SERVER_PORT, config.MAIL_TLS,
                        config.MAIL_SSL, config.MAIL_USERNAME, config.MAIL_PASSWORD)
        for user in users:
            logging.debug(f"Wysyłanie maila z potwierdzenem do {user.id} ({user.email})")
            while True:
                confirmation_string = ''.join(random.choice(
                    string.ascii_letters + string.digits) for i in range(256))
                u = db_users.get_by_confirmation_string(db, confirmation_string)
                if not u:
                    break
            msg = confirmation_mail_render(
                destination_email=user.email,
                source_email=config.MAIL_FROM,
                subject="Zakaz noszenia broni - potwierdzenie założenia konta!",
                confirmation_string=confirmation_string,
            )
            try:
                s.send_mail(msg)
            except Exception as e:
                logging.error(f"Błąd wysyłki maila do {user.email}: {e}")
                pass
            else:
                logging.info(f"Wysłano potwierdzenie założeia konta"
                             f" id={user.id} ({user.email})")
                user.confirmation = confirmation_string
                db_users.update(db, user)
    db.close()


def process_event_from_db():
    db = SessionLocal()
    db_acts = LegalActCRUD()
    new_acts = db_acts.get_notif_not_started(db)
    orphans = db_acts.get_notif_unfinished(db)
    db.close()
    if new_acts:
        for act in new_acts:
            process_event(act)
    else:
        logging.debug("Brak zdarzeń do notyfikacji")
    if orphans:
        logging.warning("Przetwarzanie osieroconych zdarzeń do notyfkacji")
        for orphan in orphans:
            process_event(orphan)


def process_event(act: LegalAct):
    start_time = time.time()
    config = get_config()
    db = SessionLocal()
    db_acts = LegalActCRUD()
    db_users = UserCRUD()
    db_notif = NotificationCRUD()
    s = SmtpWrapper(config.MAIL_SERVER, config.MAIL_SERVER_PORT, config.MAIL_TLS,
                    config.MAIL_SSL, config.MAIL_USERNAME, config.MAIL_PASSWORD)
    smtp_errors = 0
    count = 0
    mail_delay = config.MAIL_SEND_DELAY

    if act.year < 2023:
        logging.error(f"Zgłoszono notyfikacje do zdarzenia z przeszłości: {act.year}")
        db.close()
        return

    logging.debug(f"przetwarzanie notyfikacji dla rozporzadzenia id={act.id}")
    if act.notif_finished_proc:
        logging.warning(f"Rozporzadzenie o id={act.id} zostało już przetworzone")
        db.close()
        return

    act.notif_started_proc = datetime.now()
    act = db_acts.update(db, act)  # start timestamp
    users = db_users.get_users_to_notify(db, act.id)
    for u in users:
        msg = notification_mail_render(
            destination_email=u.email,
            source_email=config.MAIL_FROM,
            subject="Zakaz noszenia broni - nowy!",
            date=act.published_date,
            number=act.number,
            year=act.year,
            pdf_url=act.pdf_url,
            unregister_key=u.confirmation,
        )
        try:
            s.send_mail(msg)
        except Exception as e:
            logging.error(f"Błąd wysyłki maila do {u.email}: {e}")
            smtp_errors += 1
            pass
        else:
            db_notif.create(db, user_id=u.id, act_id=act.id)
            logging.info(f"notyfikacja użytkownika id={u.id} ({u.email}) o rozp. "
                         f"{act.number}/{act.year}")
            count += 1
        time.sleep(mail_delay)
    logging.info(f"notyfikowano {count} użytkowników"
                 f" w czasie {time.time()-start_time:.4f} s.")
    if smtp_errors == 0:
        act.notif_finished_proc = datetime.now()
        db_acts.update(db, act)  # finish timestamp
    logging.info(f"wykryto {smtp_errors} błędów smtp,"
                 f" {s.reconnects} ponawianych połączeń.")
    db.close()
