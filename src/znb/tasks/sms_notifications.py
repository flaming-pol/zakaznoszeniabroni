"""Moduł obsługi powiadomień SMS."""

import datetime
import logging

from enum import Enum
from jinja2 import Environment, PackageLoader

from znb.config import get_config
from znb.db import LegalActCRUD, SmsContactCRUD, SmsNotificationCRUD
from znb.db.session import SessionLocal
from znb.models import LegalAct, SmsNotificationCapability
from znb.sms.providers.smsplanet import SMSPlanet_API


class Miesiac(Enum):
    styczen = 1
    luty = 2
    marzec = 3
    kwiecien = 4
    maj = 5
    czerwiec = 6
    lipiec = 7
    sierpien = 8
    wrzesien = 9
    pazdziernik = 10
    listopad = 11
    grudzien = 12


def process_sms_alerts():
    config = get_config()
    if not config.SMS_ENABLED:
        logging.debug("Moduł wysyłki SMS wyłączony")
        return
    db_session = SessionLocal()
    db_acts = LegalActCRUD()
    j2_env = Environment(loader=PackageLoader("znb.sms", "templates"))
    template_sms = j2_env.get_template("sms_alert.j2")

    logging.debug("Przetwarzanie alertów SMS")
    acts = db_acts.get_sms_alert_capable(db_session)
    for a in acts:
        if a.enriched:
            sms_message = template_sms.render(id=a.id)
        else:
            sms_message = template_sms.render()
        status = send_sms(a, soft_id_prefix="Alert", message=sms_message)
        if status is True:
            a.notif_sms_cap = SmsNotificationCapability.reminder
            db_acts.update(db_session, a)
    db_session.close()


def process_sms_remind():
    config = get_config()
    if not config.SMS_ENABLED:
        logging.debug("Moduł wysyłki SMS wyłączony")
        return
    db_session = SessionLocal()
    db_acts = LegalActCRUD()
    j2_env = Environment(loader=PackageLoader("znb.sms", "templates"))
    template_sms = j2_env.get_template("sms_reminder.j2")

    logging.debug("Przetwarzanie przypomnień SMS")
    acts = db_acts.get_sms_remind_capable(db_session)
    for a in acts:
        times_array = []
        details = a.detail
        if details:
            for d in details:
                times = d.time
                if times:
                    for t in times:
                        times_array.append(t.begin)
        times_array.sort()
        if not times_array:
            logging.error("Przypomnienie SMS nieudane. Brak odczytej daty "
                          f"obowiązywania zakazu. (id={a.id})")
            continue
        now = datetime.datetime.now()
        t = times_array[0]
        time_diff = now - t
        # odjecie od daty aktualnej daty z przyszlosci daje wynik mniejszy od 0
        if time_diff.total_seconds() > 0 and now.hour >= 7:
            # Wysyła przypomnienie w:
            #  dniu zaczęcia obowiązywania zakazu
            #  około godziny 7
            sms_message = template_sms.render(id=a.id)
            status = send_sms(a, soft_id_prefix="Remind", message=sms_message)
            if status is True:
                a.notif_sms_cap = SmsNotificationCapability.non
                db_acts.update(db_session, a)
        else:
            logging.info(f"Przypomnienie SMS dla id={a.id} status: OCZEKUJE!")
    db_session.close()


def send_sms(affected_act: LegalAct, soft_id_prefix: str, message: str) -> bool:
    db_session = SessionLocal()
    db_contacts = SmsContactCRUD()
    db_notifications = SmsNotificationCRUD()
    phone_numbers = []

    config = get_config()
    api = SMSPlanet_API(
        token=config.SMS_API_TOKEN,
        from_field=config.SMS_API_FROM_FIELD
    )

    sms_name = f"{soft_id_prefix} {affected_act.number}/{affected_act.year} ({affected_act.id})"
    existing_notif = db_notifications.get_by_soft_id(db_session, sms_name)
    if existing_notif:
        logging.error(f"Notyfikacja SMS dla rozporządzenia id={affected_act.id} już wysłana!")
        db_session.close()
        return False
    contacts = db_contacts.get_all(db_session, only_active=True)
    for c in contacts:
        phone_numbers.append(str(c.phone_number))
    logging.info(f"Wysyłanie SMS {sms_name} do odbiorców: {phone_numbers}")
    try:
        status = api.send(
            contacts=phone_numbers,
            message=message,
            report_name=sms_name,
            demo=config.SMS_DEMO_MODE
        )
        logging.info(f"Wiadomosc SMS: {message}")
    except Exception as e:
        logging.error(f"Wysyłanie SMS dot rozp. {affected_act.id} zakończone błędem: {e}!")
        db_session.close()
        return False
    else:
        db_notifications.create(db_session, sms_name, affected_act.id)
        logging.info(f"Wysyłanie SMS dot rozp. {affected_act.id} zakończone poprawnie! "
                     f"MessageId: {status}")
        db_session.close()
        return True


def test_sms():
    now = datetime.datetime.now()
    if now.day != 1:
        return
    db_session = SessionLocal()
    db_contacts = SmsContactCRUD()
    phone_numbers = []

    config = get_config()
    api = SMSPlanet_API(
        token=config.SMS_API_TOKEN,
        from_field=config.SMS_API_FROM_FIELD
    )
    month = Miesiac(now.month)
    contacts = db_contacts.get_all(db_session, only_active=True)
    db_session.close()
    for c in contacts:
        phone_numbers.append(str(c.phone_number))
    logging.info(f"Wysyłanie TEST SMS do odbiorców: {phone_numbers}")
    try:
        api.send(
            contacts=phone_numbers,
            message=f"Test systemu: {month.name}",
            report_name=f"T-{month.name}/{now.year}",
            demo=config.SMS_DEMO_MODE
        )
    except Exception as e:
        logging.error(f"Wysyłanie SMS test zakończone błędem: {e}!")
