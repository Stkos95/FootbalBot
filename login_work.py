import requests
from bs4 import BeautifulSoup as bs
from config import load_config

config = load_config()

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
}
#
LOGIN = config.other.login_lmfl
PASSWORD = config.other.login_password


login_data = {

'login-form[login]': LOGIN,
'login-form[password]': PASSWORD,
'login-form[rememberMe]': '0'
}



with requests.Session() as s:
    url = 'http://lmfl.ru/user/login'
    r = s.get(url, headers=headers)
    src = r.content
    soup = bs(src, 'html5lib')
    csrf = soup.find('input', attrs={'name':'_csrf'})['value'] # Делаю запрос на страницу входа, получаю значение 'value' поля ввода


    login_data['_csrf'] = csrf # Полученное значение добавляю в словарь с данными для последующего POST запроса




    r = s.post(url, data=login_data, headers=headers)
    r = s.get('http://lmfl.ru/cp/tournament/search', params={'TournamentSearch[name]': 22})
    #
    # list_of_tournaments = {}
    #
    # src = r.content
    # soup = bs(src, 'html5lib')
    # data = soup.find_all('li', class_='list-group-item')
    # for ind, val in enumerate(data):
    #     name_of_tournament = val.find('h4').text
    #     tags_a = val.find_all('a')
    #     link = list(filter(lambda x: x.text.strip() == 'Команды', val.find_all('a')))[0].get('href')
    #     list_of_tournaments.update({ind + 1: {'name': name_of_tournament,
    #                                           'link': link}})
    # print(list_of_tournaments)
