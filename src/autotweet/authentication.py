import pickle
import logging

from constance import config

from autotweet.driver import getChromeRemoteDriver
from autotweet.utils import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common import action_chains, keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

def ok_email(email=None, driver=None):
    sleep()
    if not driver or not email:
        return
    if config.email_verification in driver.page_source:
        try:
            driver.find_element_by_xpath(
                '//input[@id="challenge_response"]'
                ).send_keys(email)
            sleep()
            _submit_button = driver.find_element_by_xpath(
                '//input[@id="email_challenge_submit"]'
                ).click()
        except NoSuchElementException:
            logger.error('Email verification failed')
            return
        sleep()

def ok_phone(phone=None, driver=None):
    sleep()
    source = driver.page_source
    logger.warn(f" Page source: {source[:500]}")
    if config.phone_verification in source:
        try:
            driver.find_element_by_xpath(
                '//input[@id="challenge_response"]'
                ).send_keys(phone.as_e164 )
            sleep()
            driver.find_element_by_xpath(
                '//input[@id="email_challenge_submit"]'
                ).click()
        except NoSuchElementException:
            logger.error('Phone verification failed')
            return
    sleep()

def login_twitter(username=None, password=None, driver=None):
    driver.get("https://twitter.com/login")
    sleep()
    focused_elem = driver.switch_to.active_element
    focused_elem.send_keys(username)
    sleep()
    focused_elem.send_keys(keys.Keys.TAB)
    focused_elem = driver.switch_to.active_element
    focused_elem.send_keys(password)
    sleep()
    focused_elem.send_keys(keys.Keys.TAB)
    focused_elem = driver.switch_to.active_element
    focused_elem.click()

def authenticate(username, password, driver, email, phone):
    login_twitter(
        username=username,
        password=password,
        driver=driver
    )
    ok_email(email=email, driver=driver)
    ok_phone(phone=phone, driver=driver)

def get_auth_driver_chrome(community):
    username = community.account.username
    password = community.account.password
    phone = community.account.phone
    email = community.account.email
    cookies = community.account.cookies
    if not password or not username:
        return
    driver = getChromeRemoteDriver()
    if not driver:
        return
    driver.get("https://www.twitter.com")
    sleep()
    if cookies:
        cookie_lst = pickle.loads(cookies)
        for cookie in cookie_lst:
            driver.add_cookie(cookie)
        driver.get("https://twitter.com/settings/account")
        try:
            login_redirect = EC.url_to_be('https://twitter.com/login')
            WebDriverWait(driver, 5).until(login_redirect)
            authenticate(username, password, driver, email, phone)
        except TimeoutException:
            print("Timed out waiting for page to load")
    else:
        authenticate(username, password, driver, email, phone)
    logger.debug(f"{driver.page_source}")
    if not cookies:
        cookies = pickle.dumps(driver.get_cookies())
        account = community.account
        account.cookies = cookies
        account.save()
    return driver