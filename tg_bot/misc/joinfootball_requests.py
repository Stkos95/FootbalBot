import requests
import json
from dataclasses import dataclass
from typing import List
from tg_bot.query_statements import QUERY_ALL_PLAYERS
from config import load_config

config = load_config()
# Отредактировать файл, использовать созданные query_statements, пересмотреть алгоритм отбора игрока

TOKEN_MEN = config.joinsport.token

# Файл используется в проверке игроков в процессе добавления в команду.


@dataclass
class Player:
    id: str
    full_name: str
    birthday: str
    photo: str


class JoinSportApi:
    '''
    class gets connection to Joinsport api and allow to get list of all players
    in database.
    '''
    URL = 'https://api.joinsport.io/graphql'
    headers = {'Api-key': TOKEN_MEN}

    def _make_request(self, q: str, var: None | str = None):
        data = {'query': q}
        if var:
            data.update(variables=var)
        r = requests.post(self.URL, headers=self.headers, json=data)
        return json.loads(r.text)


    def get_all_players_list(self) -> List[Player]:
        r = self._make_request(QUERY_ALL_PLAYERS)
        players = r['data']['frontend']['players']['data']
        res = [Player(
                id=player.get('player_id'),
                full_name=' '.join([player[i].strip() for i in player if i.endswith('name')]),
                birthday = player.get('birthday'),
                photo = player.get('photo')
                    ) for player in players]
        return res



class GetJoinfootball(JoinSportApi):
    def __init__(self):
        self.players = self.get_all_players_list()

    def get_player_1(self, fio: str) -> List[Player]:
        """

        :param fio: fio of player you check
        :return: {player_id: {'name': Иванов Иван, 'birthday': 10.05.2000}}
        """

        players = self.get_all_players_list()
        fio_splitted = fio.split()
        players_copy = players.copy()

        for name in fio_splitted:
            for player in players:
                if name not in player.full_name:
                    players_copy.remove(player)
            players = players_copy[:]
        return players_copy


if __name__ == '__main__':

    d = GetJoinfootball()
    z = d.get_player_1('Константин Андреевич')
    print(z)
