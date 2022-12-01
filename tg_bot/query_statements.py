from config import load_config
import requests
import json
conf = load_config()

QUERY_ROUND = ''' query
         frontend ($round_id: ID!) {
            frontend {
                round(round_id:$round_id){
                    series_type
                    series_length
                    name
                    target
                    has_table

                    calendar{
                        match_id
                        tour
                        number
                        team1{
                            full_name
                            }
                        team2{
                            full_name
                            }
                    }
                    teams{
                        team_id
                        full_name
                        logo
                        }
                    }
                } 
            }
            '''


QUERY_TOURNAMENT = '''
        query frontend($tournament_id: ID!) {
        frontend {
            tournament(tournament_id:$tournament_id){

                applications{
                    status
                    team{
                    full_name
                    team_id
                    }
                }
                tournament_id
                season_id
                full_name
                rounds{
                    round_id
                    name
                }  
            }
        } 
    }

'''
QUERY_TEAM = ''' query
         frontend ($team_id: ID!) {
            frontend {
                team(team_id:$team_id){
                        players{
                            player_id
                            last_name
                            first_name
                            middle_name
                            birthday
                            photo
                            application{
                                status
                            }
                        }
                    }
                }
            } 
            '''

QUERY_ALL_TOURNAMENTS = '''
query frontend {
        frontend {
            tournaments(first:1025285){
                data{
                    tournament_id
                    full_name
                    is_published
                }
            }
        } 
    }

'''


QUERY_APPLICATION = ''' query
 frontend($team_id: ID!, $tournament_id: ID!)  {
    frontend {
        application(tournament_id:$tournament_id, team_id:$team_id){
            tournament_id
            team_id
            status
            name
            team{
                players{
                    player_id
                    last_name
                    first_name
                    middle_name
                    application{
                        player_id
                        status
                        
                    }
                }
            }
            players{
                status
                player{
                    last_name
                    first_name
                    middle_name
                    player_id
                    
                }
            }
        } 
    } }
    '''

def get_data(q,token, var=None):
    headers = {
        'Api-key': token
    }
    data = {'query': q}
    if var:
        data.update(variables=var)

    r = requests.post(conf.joinsport.url, headers=headers, json=data)
    return json.loads(r.text)


def get_query(query,token, **args):
    var = args
    query_result = get_data(query, token, var=var)['data']['frontend']
    return query_result

d = get_query(QUERY_APPLICATION, conf.joinsport.token, tournament_id=1025285, team_id=1203706)

from pprint import pprint
