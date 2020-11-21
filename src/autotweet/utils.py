import time
import ast
import random
import requests
import logging
import string

from constance import config

from selenium.common.exceptions import NoSuchElementException
from autotweet.driver import getOrCreateWebdriver
from selenium.webdriver.common.action_chains import ActionChains

logger = logging.getLogger(__name__)

def randinterval(low, high):
    return random.randint(low, high)/1000

"""Sleep for a random time between low and high milliseconds
"""
def sleep(low=1500, high=3000):
    '''
    Sleep during a random amount of time between low and high milliseconds.

            Optional parameters:
                    low (int): A decimal integer representing the lower limit
                    in milliseconds
                    high (int): A decimal integer representing the higher limit
                    in milliseconds

            Returns:
                    None
    '''
    time.sleep(randinterval(low, high))
    
def ok_click(driver=None):
    if not driver:
        driver = getOrCreateWebdriver(js=False)
    sleep()
    try:
        button = driver.find_element_by_xpath('//button[@type="submit"]')
        button.click()
    except NoSuchElementException:
        return
    sleep()
    
def get_selenium_firefox_headers():
    headers: str = config.selenium_firefox_headers
    try:
        return ast.literal_eval(headers)
    except SyntaxError as e:
        if not headers:
            logger.error(
                f"'headers' constance setting string appears to be empty"
            )
        else:
            logger.error(f"error while evaluating headers string: {e}")
        return {}
    except Exception as e:
        logger.error(f"{e}")
        return {}

def send_post_request(auth_token=None, url=None, commit=None, referer=None):
    headers = get_selenium_firefox_headers()
    headers["Referer"]=referer
    driver = getOrCreateWebdriver(js=False)
    cookies = driver.get_cookies()
    s = requests.Session()
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])
    response = s.post(
        url,
        data={
            "authenticity_token":auth_token,
            "commit":commit
        },
        headers=headers
    )
    logger.debug(
        f"code: {response.status_code}\n"
        f"json: {response.text}\n"
        f"headers: {response.headers}\n"
    )
    return response

def rnd_str_gen(size=6, chars= string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def tweet(txt, driver=None):
    if not driver:
        driver = getOrCreateWebdriver(js=False)
    sleep()
    try:
        driver.find_element_by_xpath('//a[@href="/compose/tweet"]').click()
    except NoSuchElementException:
        return
    try:
        tweet_box = driver.find_element_by_xpath(
            '//textarea[@name="tweet[text]"]'
        )
    except NoSuchElementException:
        return
    tweet_box.send_keys(txt)
    sleep()
    try:
        driver.find_element_by_xpath('//input[@value="Tweet"]').click()
    except NoSuchElementException:
        return
    
def tweet_desktop(txt, driver=None):
    if not driver:
        driver = getOrCreateWebdriver(js=False)
    sleep()
    try:
        driver.find_element_by_xpath('//a[@href="/compose/tweet"]').click()
    except NoSuchElementException:
        return
    focused_elem = driver.switch_to.active_element
    focused_elem.send_keys(txt)
    sleep()
    try:
        tweet_button_span = driver.find_element_by_xpath('//span[text()="Tweet"]')
    except NoSuchElementException:
        return
    action = ActionChains(driver) 
    # perform the operation 
    action.move_to_element(tweet_button_span).click().perform() 