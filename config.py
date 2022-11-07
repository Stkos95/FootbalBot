from environs import Env
from dataclasses import dataclass
from typing import List

env = Env()
env.read_env()


@dataclass
class Database:
    host_address: str
    username: str
    password: str
    db_name: str

@dataclass
class Config:
    token: str
    admin: int
    database: Database





def load_config():
    env = Env()
    env.read_env()
    return Config(
        token = env.str('TOKEN'),
        # admins = list(map(int, env.list('ADMINS')))
        admin = env.int('ADMINS'),
        database=Database(
            host_address=env.str('HOST_ADDRESS'),
            username=env.str('USERNAME'),
            password=env.str('PASSWORD'),
            db_name=env.str('DB_NAME')

        )
    )


