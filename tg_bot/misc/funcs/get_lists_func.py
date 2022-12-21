from sqlalchemy import select, distinct
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from tg_bot.misc.database.models import Tournaments
from tg_bot.misc.image_processing.get_list_teams import process_players
from tg_bot.misc.database.db import Session

def get_tournaments(session):
    statement1 = select(distinct(Tournaments.tournament_id), Tournaments.name_tournament)
    tournaments = session.execute(statement1).all()
    return tournaments

def get_squad(team_id):
    with Session() as session:
        players = process_players(team_id)
    return players

def get_squad_answer(players):
    answer = 'Список игроков:\n'
    text = [f"{indx + 1} - {player.get('name')}" for indx, player in enumerate(players.values())]
    answer += '\n'.join(text)
    return answer