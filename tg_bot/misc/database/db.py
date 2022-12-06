from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, select
from sqlalchemy import text
from .models import Base, Users, Teams
from config import load_config

config = load_config()


# URLDATABASE = f'postgresql+psycopg2://{config.database.username}:{config.database.password}@{config.database.host_address}/{config.database.db_name}'

URLDATABASE = f'postgresql+psycopg2://guest:qazwsx123@54.209.125.62:5432/men'

def get_engine_connection(URLDATABASE=URLDATABASE):
    engine = create_engine(URLDATABASE, future=True)
    Base.metadata.create_all(engine)
    session = sessionmaker(engine, future=True)
    return session


