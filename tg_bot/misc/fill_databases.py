import requests
import json
from sqlalchemy import select
from tg_bot.query_statements import QUERY_TOURNAMENT, get_query, QUERY_ALL_TEAMS, QUERY_ROUND
from tg_bot.misc.image_processing.get_list_teams import get_current_tournaments_list, check_rounds_for_futsal
from tg_bot.misc.database.db import get_engine_connection
from tg_bot.misc.database.models import Tournaments, Base, Teams, TeamTournaments

regular_tournaments = (1025285, 1026113)
URL = 'https://api.joinsport.io/graphql'
TOKEN_WOMEN = 'jn46S5a8AJ3A4EJrek5aTRpepngErQtGEdCkD6dYd8gJJmvzhcLmryd1an6JnhTg'
TOKEN_MEN = 'fg376cGJypQHkEsU3VCuPHVbQxQQeQM3mXCUW9pJEddBN4yRsKzw9rKmE42kPk8Q'

headers = {
    'Api-key': TOKEN_MEN
}
Session = get_engine_connection()



def add_tournaments_database(session):
    tournaments = get_current_tournaments_list()
    for tournament in tournaments:
        process_tournament(session, tournament)

def process_tournament(session,tournament):
    rounds = check_rounds_for_futsal(int(tournament.get('tournament_id')))
    for round_ in rounds:
        tournament_id,round_id = process_round_and_add_db_and_return_ids(session,tournament,round_)
        process_teams_in_round_and_add_to_db(session, tournament_id, round_id)



def process_round_and_add_db_and_return_ids(session,tournament, round_):
    tournament_name = tournament.get('full_name')
    tournament_id = int(tournament.get('tournament_id'))
    round_id = int(round_.get('round_id'))
    round_name = round_.get("name")
    add_to_db(session,
              Tournaments(
                  tournament_id=tournament_id,
                  round_id=round_id,
                  name_tournament=tournament_name,
                  name_round=round_name,
                  start_date=tournament.get('start_dt'),
                  end_date=tournament.get('end_dt')
              )
              )
    return tournament_id, round_id


def process_teams_in_round_and_add_to_db(session, tournament_id, round_id):
    teams_in_round = add_applications(round_id)['round']['teams']
    for team in teams_in_round:
        team_id = int(team.get('team_id'))
        add_to_db(session,
                  TeamTournaments(
                      team_id=team_id,
                      tournament_id=tournament_id,
                      round_id=round_id

                  ))







def get_all_teams():
    r = get_query(query=QUERY_ALL_TEAMS,token=TOKEN_MEN)['teams']['data']
    return r


def add_teams_database(session):
    teams = get_all_teams()
    for team in teams:

        if not team.get('full_name').startswith('Место'):
            add_to_db(session,
                Teams(
                    team_id=team.get('team_id'),
                    team_name=team.get('full_name')
                )
            )



def add_to_db(session, item):
    try:
        session.add(item)
        session.flush()
        session.commit()
    except:
        pass



def add_applications(round_id):
    r = get_query(query=QUERY_ROUND,token=TOKEN_MEN, round_id=round_id)
    return r

def add_data_to_database():
    with Session() as session:
        add_tournaments_database(session)
        # add_teams_database(session)

# add_data_to_database()

#
# def add_rounds(token, session):
#     tournaments = get_current_tournaments_list()
#     for tournament in tournaments:
#         tournament_id = int(tournament.get('tournament_id'))
#         if tournament_id in regular_tournaments:
#             rounds = check_rounds_for_futsal(tournament_id)
#             for round_ in rounds:
#                 round_id = round_.get('round_id')
#                 r = get_query(QUERY_ROUND, token, round_id=round_id)
#                 add_to_db(session, Rounds(
#                     round_id=round_id,
#                     round_name=r['round']['name'],
#                     tournament_id=tournament_id
#                 ))
#                 session.commit()
#             print(rounds)

# with Session() as session:
#     add_rounds(TOKEN_MEN, session)





#--------------------- этапы (турниры) только по футзалу 22/23

#
# def prepare_teams():
#     query = '''query frontend {
#             frontend {
#                 tournament(tournament_id:1025285){
#                     tournament_id
#                     full_name
#                     start_dt
#                     end_dt
#                     rounds{
#                         round_id
#                         name
#                     }
#                 }
#             } }'''
#     r = requests.post(URL, headers=headers, json={'query': query})
#     results = json.loads(r.text)
#     print(results)
#     rounds = results['data']['frontend']['tournament']['rounds']
#     print(rounds)
#
#
#
#
#     Session = get_engine_connection()
#
#     with Session() as session:
#         for rang, round in enumerate(rounds):
#             id_tour, name_tour = round['round_id'], round['name']
#             session.add(Tournaments(tournament_id=id_tour, name=name_tour, rangs=rang+1))
#
#         session.commit()
#     #--------------------------------------
#
#     query = '''
#     query frontend {
#             frontend {
#                 tournament(tournament_id:1025285){
#                     rounds{
#                         round_id
#                         name
#                     }
#                 }
#
#             } }
#
#     '''
#
#     r = requests.post(URL, headers=headers, json={'query': query})
#     results = json.loads(r.text)
#     rounds = results['data']['frontend']['tournament']['rounds']
#
#     rounds = [i.get('round_id') for i in rounds]
#
#
#
#
#
#
#
#     # получил список турниров
#     with Session() as session:
#         state = select(Tournaments.tournament_id)
#         rounds = session.execute(state).scalars().all()
#
#     for round in rounds:
#
#         query = ''' query
#          frontend ($round_id: ID!) {
#             frontend {
#                 round(round_id:$round_id){
#                     teams{
#                         team_id
#                         full_name
#                     }
#                 }
#
#             } }
#             '''
#         var = {'round_id': round}
#     # Получил список команд по каждому турниру\раунду
#         r = requests.post(URL, headers=headers, json={'query': query, 'variables': var})
#         teams = json.loads(r.text)['data']['frontend']['round']['teams']
#         print(teams)
#         with Session() as session:
#             to_add = [Teams(team_id=int(team['team_id']), team_name=team['full_name'], tournament_id=int(round)) for team in teams]
#             session.add_all(to_add)
#             session.commit()
#             stm = select(Tournaments)
#             # print(session.execute(stm).all())
#     print('ready')
#     return Session




