import logging
import sys

from logging.handlers import TimedRotatingFileHandler

from znb.config import get_config


def setup_logging(filename='logs/znb.log'):
    config = get_config()

    log_level_template = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    log_level = log_level_template.get(config.LOG_LEVEL)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(log_level)

    file_handler = TimedRotatingFileHandler(filename=filename,
                                            interval=1,
                                            when='midnight',
                                            encoding='utf-8',
                                            utc=False,
                                            backupCount=10)
    file_handler.setLevel(log_level)
    handlers = [file_handler, stdout_handler]
    # handlers = [file_handler]
    # handlers = [stdout_handler]
    logging.basicConfig(handlers=handlers,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        level=log_level,
                        datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
