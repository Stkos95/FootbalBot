# here we log in on site and get authorised cookies.
import requests

from config import load_config
from bs4 import BeautifulSoup as bs
from selenium import webdriver
# from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


config = load_config()

LOGIN = config.other.login_lmfl
PASSWORD = config.other.password_lmfl


def initiate_driver():
    service = Service(executable_path=ChromeDriverManager().install())
    option = Options()
    option.add_argument("start-maximized")
    option.add_experimental_option('detach', True)
    # option.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=option)
    return driver

def authorise(remember_me: bool = False):
    driver = initiate_driver()
    driver.get('http://lmfl.ru/user/login')
    if remember_me:
        driver.find_element(by=By.XPATH, value='/html/body/div/div[3]/div/div[1]/form/div[3]/label').click()
    driver.find_element(by=By.ID, value='login-form-login').send_keys(LOGIN)
    driver.find_element(by=By.ID, value='login-form-password').send_keys(PASSWORD)
    driver.find_element(by=By.XPATH, value='/html/body/div/div[3]/div/div[1]/form/button').click()
    return driver


def get_authorized_cookie():
    dr = authorise(remember_me=True)
    time.sleep(2)
    cookie_driver = dr.get_cookies()
    return cookie_driver



