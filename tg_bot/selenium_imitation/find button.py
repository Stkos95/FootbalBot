from log_in import authorise






team_id = '1255301'
player_id = '5199673'
players_status = ['left', 'accepted', 'available']
status = None

team_link = f'http://lmfl.ru/team/backend/players?id={team_id}&status={status}'




driver = authorise()
driver.get('')

