from environs import Env
from dataclasses import dataclass
from typing import List

env = Env()
env.read_env()

@dataclass
class Config:
    token: str
    admins: List[int]


def load_config():
    env = Env()
    env.read_env()
    return Config(
        token = env.str('TOKEN'),
        admins = list(map(int, env.list('ADMINS')))
    )

