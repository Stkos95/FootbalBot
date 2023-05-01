from log_in import authorise
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



team_id = '1255301'
player_id = '5199673'
players_status = ['left', 'accepted']
status = None






driver = authorise()
time.sleep(1)
for status in players_status:
    try:
        team_link = f'http://lmfl.ru/team/backend/players?id={team_id}&status={status}'
        driver.get(team_link)
        driver.save_screenshot('scren.png')
        d = driver.find_element(by=By.XPATH, value=f'//a[@data-player_id="{player_id}"]')
    except Exception as e:

        print(f'{status} не найдено')
    else:
        d.click()
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//button[@data-bb-handler="confirm"]')))
        d = driver.find_element(by=By.XPATH, value='//button[@data-bb-handler="confirm"]').click()
        break