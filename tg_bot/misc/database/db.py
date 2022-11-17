from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import text
from .models import Base
from config import load_config

config = load_config()


URLDATABASE = f'postgresql+psycopg2://{config.database.username}:{config.database.password}@{config.database.host_address}/{config.database.db_name}'


def get_engine_connection():
    engine = create_engine(URLDATABASE, future=True)
    Base.metadata.create_all(engine)
    session = sessionmaker(engine, future=True)
    return session


