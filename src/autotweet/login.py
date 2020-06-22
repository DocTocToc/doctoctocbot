"""login.py

This module performs a programmatical login into a Twitter account using
Selenium.

"""

import argparse
import time
import string
import random
from constance import config
import logging
import requests
import sys

from selenium.webdriver.common.by import By
from selenium.webdriver.common import action_chains, keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

from bot.models import Account

from autotweet.driver import getOrCreateWebdriver
from autotweet.utils import sleep
from autotweet.utils import ok_click
from autotweet.utils import send_post_request

logger = logging.getLogger(__name__)

def rnd_str_gen(size=6, chars= string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class AutoLogin:
    def __init__(self, username):
        if not username:
            return
        self._username = username
        logger.debug(f"{self._username}")
        try:
            account = Account.objects.get(username=self._username)
            logger.debug(f"{account} {account.username} {account.password}")
        except Account.DoesNotExist:
            return
        self._password = account.password
        self._email = account.email
        self._authenticity_token = None
        self._driver = getOrCreateWebdriver(js=False)
    def ok_email(self):
        if not self._email:
            logger.error(f"Email field for  @{self._username} is empty.")
            return
        sleep()
        source = self._driver.page_source
        logger.warn(f" Page source: {source}")
        if config.email_verification in source:
            try:
                self._driver.find_element_by_xpath(
                    '//input[@id="challenge_response"]'
                    ).send_keys(self._email)
                sleep()
                self._driver.find_element_by_xpath(
                    '//input[@id="email_challenge_submit"]'
                    ).click()
            except NoSuchElementException:
                logger.error('Email verification failed')
                return
            sleep()
    def get_authenticity_token(self):
        if self._authenticity_token:
            return self._authenticity_token
        try:
            auth_elem = self._driver.find_element_by_xpath(
                '//input[@name="authenticity_token"]'
            )
        except NoSuchElementException:
            logger.error('Authenticity token not found')
            return            
        auth_token = auth_elem.get_attribute('value')
        self._authenticity_token = auth_token
        return auth_token
    def login_mobile_twitter(self):
        if not self._password:
            logger.error(f"Password field for  @{self._username} is empty.")
            return
        #driver = getOrCreateWebdriver(js=False)
        self._driver.get("https://mobile.twitter.com/login")
        ok_click()
        sleep()
        username_input = self._driver.find_element_by_xpath('//input[@id="session[username_or_email]"]')
        password_input = self._driver.find_element_by_xpath('//input[@id="session[password]"]')
        login_button = self._driver.find_element_by_xpath('//input[@name="commit"]')
        username_input.send_keys(self._username)
        sleep()

        password_input.send_keys(self._password)
        sleep()
        login_button.click()
        self.ok_email()
        self.get_authenticity_token()

    def login_twitter(self):
        driver = getOrCreateWebdriver(js=True)
        driver.get("https://www.twitter.com/login")
        sleep()
        focused_elem = driver.switch_to.active_element
        focused_elem.send_keys(self.username)
        sleep()
        focused_elem.send_keys(keys.Keys.TAB)
        focused_elem = driver.switch_to.active_element
        focused_elem.send_keys(self.password)
        sleep()
        focused_elem.send_keys(keys.Keys.TAB)
        focused_elem = driver.switch_to.active_element
        focused_elem.click()
    
    def logout(self):
        auth_token = self.get_authenticity_token()
        if not auth_token:
            return
        url = "https://mobile.twitter.com/session/destroy"
        commit = "Log+out"
        referer = "https://mobile.twitter.com/account"
        send_post_request(
            auth_token=auth_token,
            url=url,
            commit=commit,
            referer=referer,
        )

def close():
    driver = getOrCreateWebdriver()
    driver.close()

def tweet(txt):
    new_tweet_id = "global-new-tweet-button"
    driver = getOrCreateWebdriver()
    sleep()
    try:
        driver.find_element_by_id(new_tweet_id).click()
    except NoSuchElementException:
        driver.get("https://www.twitter.com/compose/tweet")
    focused_elem = driver.switch_to.active_element
    focused_elem.send_keys(txt)
    sleep()
    #driver.find_element_by_class_name('SendTweetsButton').click()
    driver.find_element_by_xpath("//div[@data-testid='tweetButton']").click()
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Authorize this Twitter userid.')
    parser.add_argument('integers', metavar='N', type=int, nargs='+',
                   help='a bigint user id')
    args = parser.parse_args()
    print(f"args.integers: {args.integers}")