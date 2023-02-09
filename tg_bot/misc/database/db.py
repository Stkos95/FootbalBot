from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, select
from sqlalchemy import text
from .models import Base, Admins, Users, Teams
from config import load_config

config = load_config()


URLDATABASE = f'postgresql+psycopg2://{config.database.username}:{config.database.password}@{config.database.host_address}/{config.database.db_name}'



def get_engine_connection(URLDATABASE=URLDATABASE):
    engine = create_engine(URLDATABASE, future=True)
    Base.metadata.create_all(engine)
    session = sessionmaker(engine, future=True)
    return session


Session = get_engine_connection()
# with Session() as session:
#     res = session.execute(select(Admins)).scalars().all()
#     print(res)