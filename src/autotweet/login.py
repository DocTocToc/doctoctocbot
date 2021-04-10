"""login.py

This module performs a programmatical login into a Twitter account using
Selenium.

"""

import argparse
import string
import random
from constance import config
import logging
from selenium.webdriver.common import keys
from selenium.common.exceptions import NoSuchElementException
from bot.models import Account

from autotweet.driver import getOrCreateWebdriver
from autotweet.utils import sleep

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
        try:
            self._phone = account.phone.as_e164
        except AttributeError:
            self._phone = ""
        self._authenticity_token = None
        self._driver = getOrCreateWebdriver(js=False)

    def ok_email(self):
        logger.debug("...")
        sleep()
        source = self._driver.page_source
        logger.warn(f" Page source: {source[:500]}")
        if config.email_verification in source:
            if not self._email:
                logger.error(f"Email field for  @{self._username} is empty.")
                return
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

    def ok_phone(self):
        logger.debug("...")
        sleep()
        source = self._driver.page_source
        logger.warn(f" Page source: {source[:500]}")
        if config.phone_verification in source:
            if not self._phone:
                logger.error(f"Phone field for  @{self._username} is empty.")
                return
            try:
                self._driver.find_element_by_xpath(
                    '//input[@id="challenge_response"]'
                    ).send_keys(self._phone)
                sleep()
                self._driver.find_element_by_xpath(
                    '//input[@id="email_challenge_submit"]'
                    ).click()
            except NoSuchElementException:
                logger.error('Phone verification failed')
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
        logger.debug(f"{auth_token=}")
        return auth_token

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