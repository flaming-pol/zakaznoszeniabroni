from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

from znb.config import get_config

config = get_config()
SQLALCHEMY_DATABASE_URI = URL.create("mysql+mysqlconnector", config.DB_USER,
                                     config.DB_PASS, config.DB_SERVER, config.DB_PORT,
                                     config.DB_NAME)

engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
