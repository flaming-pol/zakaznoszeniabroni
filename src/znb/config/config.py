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
    CRAWLER_INTERVAL = 1
    DELETE_USERS_INTERVAL = 12
    NOTIFICATION_SEND_INTERVAL = 1
    CONFIRMATION_MAIL_SEND_INTERVAL = 30
    MAIL_SERVER = None
    MAIL_SERVER_PORT = None
    MAIL_FROM = None
    MAIL_TLS = False

    def __init__(self):
        load_dotenv(override=False)
        self.DB_SERVER = env.get('DB_SERVER', 'localhost')
        self.DB_PORT = env.get('DB_PORT', 3306)
        self.DB_NAME = env.get('DB_NAME', 'mydb')
        self.DB_USER = env.get('DB_USER', 'user')
        self.DB_PASS = env.get('DB_PASS', 'password')
        self.LOG_LEVEL = env.get('LOG_LEVEL', 'WARNING')
        self.PARSER_YEAR = int(env.get('PARSER_YEAR', 2023))
        self.CRAWLER_INTERVAL = float(env.get('CRAWLER_INTERVAL', 1))
        self.DELETE_USERS_INTERVAL = float(env.get('DELETE_USERS_INTERVAL', 12))
        self.NOTIFICATION_SEND_INTERVAL = float(env.get('NOTIFICATION_SEND_INTERVAL', 1))
        self.CONFIRMATION_MAIL_SEND_INTERVAL = float(env.get('CONFIRMATION_MAIL_SEND_INTERVAL', 30))
        self.MAIL_SERVER = env.get('MAIL_SERVER', 'localhost')
        self.MAIL_SERVER_PORT = int(env.get('MAIL_SERVER_PORT', 1))
        self.MAIL_FROM = env.get('MAIL_FROM', 'user@server.local')
        self.MAIL_TLS = (env.get('MAIL_TLS', False) == 'True')
