from dotenv import load_dotenv
from os import environ as env


class get_config:
    DB_SERVER = None
    DB_PORT = None
    DB_NAME = None
    DB_USER = None
    DB_PASS = None
    LOG_LEVEL = None
    PARSER_YEAR = 0
    PARSER_YEAR_CURRENT = False
    CRAWLER_INTERVAL = 1
    DELETE_USERS_INTERVAL = 12
    NOTIFICATION_SEND_INTERVAL = 1
    CONFIRMATION_MAIL_SEND_INTERVAL = 30
    MAIL_SERVER = None
    MAIL_SERVER_PORT = None
    MAIL_FROM = None
    MAIL_TLS = False
    MAIL_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_SEND_DELAY = 0.1

    def __init__(self):
        load_dotenv(override=False)
        self.DB_SERVER = env.get('DB_SERVER', 'localhost')
        self.DB_PORT = env.get('DB_PORT', 3306)
        self.DB_NAME = env.get('DB_NAME', 'mydb')
        self.DB_USER = env.get('DB_USER', 'user')
        self.DB_PASS = env.get('DB_PASS', 'password')
        self.LOG_LEVEL = env.get('LOG_LEVEL', 'WARNING')
        # self.PARSER_YEAR = int(env.get('PARSER_YEAR', 2023))
        parser_year = env.get('PARSER_YEAR', 2023)
        if parser_year.isdecimal():
            self.PARSER_YEAR = int(parser_year)
        elif isinstance(parser_year, str) and parser_year == "current":
            self.PARSER_YEAR_CURRENT = True
        self.CRAWLER_INTERVAL = float(env.get('CRAWLER_INTERVAL', 1))
        self.DELETE_USERS_INTERVAL = float(env.get('DELETE_USERS_INTERVAL', 12))
        self.NOTIFICATION_SEND_INTERVAL = float(env.get('NOTIFICATION_SEND_INTERVAL', 1))
        self.CONFIRMATION_MAIL_SEND_INTERVAL = float(env.get('CONFIRMATION_MAIL_SEND_INTERVAL', 30))
        self.MAIL_SERVER = env.get('MAIL_SERVER', 'localhost')
        self.MAIL_SERVER_PORT = int(env.get('MAIL_SERVER_PORT', 25))
        self.MAIL_FROM = env.get('MAIL_FROM', None)
        self.MAIL_TLS = (env.get('MAIL_TLS', False) == 'True')
        self.MAIL_SSL = (env.get('MAIL_SSL', False) == 'True')
        self.MAIL_USERNAME = env.get('MAIL_USERNAME', None)
        self.MAIL_PASSWORD = env.get('MAIL_PASSWORD', None)
        self.MAIL_SEND_DELAY = float(env.get('MAIL_SEND_DELAY', 0.1))
