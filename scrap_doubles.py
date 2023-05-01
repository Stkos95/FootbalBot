import requests
import json
from typing import NamedTuple
from tg_bot.query_statements import QUERY_ALL_PLAYERS
# Файл используется для нахождения дублей игроков на сайте.


headers = {
'Api-Key': 'TOKEN'
}


file_to_save = NamedTuple('file_to_save', men='men_doubles.txt', women='women_doubles.txt')

query = QUERY_ALL_PLAYERS

r = requests.post(url='https://api.joinsport.io/graphql', headers=headers, json={'query': query})

players = json.loads(r.text)

players = players['data']['frontend']['players']['data']

name_players = list(map(lambda x: ' '.join(x.values()).strip(), players))
print(name_players)
doubles = []
for i in range(len(name_players)):
    for j in range(i+1, len(name_players) - 1):
        if name_players[i] == name_players[j]:
            doubles.append(name_players[i])
            break

with open(file_to_save.men, 'w') as file: # choose file to save
    for i in set(doubles):
        file.write(i + '\n')

