import time
import ast
import random
import requests
import logging
import string

from constance import config

from selenium.common.exceptions import NoSuchElementException
from autotweet.driver import getOrCreateWebdriver

logger = logging.getLogger(__name__)

def randinterval():
    return random.randint(10, 30)/10

def sleep():
    time.sleep(randinterval())
    
def ok_click():
    driver = getOrCreateWebdriver(js=False)
    sleep()
    try:
        driver.find_element_by_xpath('//button[@type="submit"]').click()
    except NoSuchElementException:
        return
    sleep()
    
def get_selenium_firefox_headers():
    headers: str = config.selenium_firefox_headers
    return ast.literal_eval(headers)

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
    logger.debug(response)
    return response

def rnd_str_gen(size=6, chars= string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def tweet(txt):
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
    