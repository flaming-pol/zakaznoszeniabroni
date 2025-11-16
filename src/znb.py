#  ZakazNoszeniaBroni.pl -- backend crawler and notifier.
#  Copyright (C) 2023-2025  mc (kontakt@zakaznoszeniabroni.pl)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import os
import requests
import schedule
import signal
import time

from znb.config import get_config
from znb.tasks import (
    parser_wrapper,
    delete_users_not_activated,
    find_unenriched,
    process_event_from_db,
    process_send_confirmation,
    process_sms_alerts,
    process_sms_remind,
    test_sms,
)
from znb.tools import check_db
from znb.tools.logging import setup_logging


def main():
    config = get_config()
    setup_logging()
    logging.warning(f"zakaznoszeniabroni.pl -- PID: {os.getpid()},"
                    f" interwał: {config.CRAWLER_INTERVAL} min.")

    check_db()
    find_unenriched(year_begin=2008)
    delete_users_not_activated()
    process_event_from_db()
    parser_wrapper()

    if config.CRAWLER_INTERVAL < 1:
        exit(0)
    schedule.every(config.CONFIRMATION_MAIL_SEND_INTERVAL).seconds.do(process_send_confirmation)
    schedule.every(config.DELETE_USERS_INTERVAL).hours.do(delete_users_not_activated)
    schedule.every(config.NOTIFICATION_SEND_INTERVAL).minutes.do(process_event_from_db)
    schedule.every(config.CRAWLER_INTERVAL).minutes.do(parser_wrapper)
    schedule.every(config.CRAWLER_INTERVAL).minutes.do(find_unenriched,
                                                       year_begin=config.PARSER_YEAR)
    schedule.every(config.CRAWLER_INTERVAL).minutes.do(process_sms_alerts)
    schedule.every(config.CRAWLER_INTERVAL).minutes.do(process_sms_remind)
    schedule.every().day.at('15:00').do(test_sms)

    signal.signal(signal.SIGINT, lambda s, f: schedule.clear())

    while True:
        schedule.run_pending()
        if not schedule.get_jobs():
            break
        time.sleep(1)


if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    main()
