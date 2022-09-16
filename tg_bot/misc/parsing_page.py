import requests
from bs4 import BeautifulSoup as bs





headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
}


login_data = {

'login-form[login]': 'stkos1331@gmail.com',
'login-form[password]': 'q1a1z1w1s1x1',
'login-form[rememberMe]': '0'
}

def get_list_of_tournaments(s: requests.Session):
    log_in(s)
    r = s.get('http://lmfl.ru/cp/tournament/search', params={'TournamentSearch[name]': 22})
    list_of_tournaments = {}
    src = r.content
    soup = bs(src, 'html5lib')
    data = soup.find_all('li', class_='list-group-item')
    for ind, val in enumerate(data):
        name_of_tournament = val.find('h4').text
        link = list(filter(lambda x: x.text.strip() == 'Команды', val.find_all('a')))[0].get('href')
        list_of_tournaments.update({ind + 1: {'name': name_of_tournament,
                                              'link': link}})
    return list_of_tournaments



def log_in(s: requests.Session):
    url = 'http://lmfl.ru/user/login'
    r = s.get(url, headers=headers)
    src = r.content
    soup = bs(src, 'html5lib')
    csrf = soup.find('input', attrs={'name': '_csrf'})[
        'value']  # Делаю запрос на страницу входа, получаю значение 'value' поля ввода
    login_data['_csrf'] = csrf  # Полученное значение добавляю в словарь с данными для последующего POST запроса
    r = s.post(url, data=login_data, headers=headers)



def get_list_of_teams(s: requests.Session):
    list_of_teams = dict
    r = s.get('http://lmfl.ru/cp/tournament/1017964/application/select-team')
    soup = bs(r.content, 'html5lib')
    teams = soup.find('div', id='teams-approved').find_all('h4')
    list_of_teams = {team.find('a').text.strip() : f'http://lmfl.ru{team.find("a").get("href")}' for team in teams}
    # for team in teams:
    #     info = team.find('a')
    #     link ='http://lmfl.ru' + info.get('href')
    #     name = info.text
    return list_of_teams

def add_player_to_team(s: requests.Session, link_add_player):
    """описать функцию для добавления игрока в команду, когда уже выбрана команда."""
    r = s.get(link_add_player, headers=headers)
    soup = bs(r.content, 'html5lib')
    '''Доделать'''







