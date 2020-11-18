import re
import logging
from typing import List, Optional
import http.client

import numpy as np
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.webdriver.common import action_chains, keys
from selenium.common.exceptions import NoSuchElementException
from bot.lib.statusdb import Addstatus
from autotweet.utils import sleep
from autotweet.driver import getChromeRemoteDriver
from community.models import Community
from conversation.models import Tweetdj, Treedj
from community.helpers import (
    get_community_bot_socialuser,
    get_community_twitter_tweepy_api
)
from conversation.models import create_leaf, create_tree

logger = logging.getLogger(__name__)


def exists(site, path):
    conn = http.client.HTTPSConnection(site)
    conn.request('HEAD', path)
    response = conn.getresponse()
    conn.close()
    return response.status == 200


class ReplyCrawler(object):
    def __init__(self, community, sids):
        self.community = community
        self.driver = get_auth_driver_chrome(self.community)
        self.sids = sids

    def get_tree_nodes(self, status_id):
        all_nodes: List[int] = []
        new_nodes: List[int] = []
        old_nodes: List[int] = []
        protocol = "https://"
        site = "twitter.com"
        path = f"/i/web/status/{status_id}"
        #if not exists(site, path):
        #    logger.error(f"Status {status_id} does not exist.")
        #    return
        url = protocol + site + path
        #driver.set_page_load_timeout(10)
        self.driver.maximize_window()
        self.driver.get(url)
        sleep(750, 1250)
        counter = 0
        self.clickShowReplies()
        while True:
            links = self.driver.find_elements_by_tag_name("a")
            hrefs = [link.get_attribute("href") for link in links]
            for href in hrefs:
                #logger.debug(f"{href=}")
                id_regex = re.search("\/.*\/status(?:es)?\/([^\/\?]+)", href)
                if id_regex and ("/photo/" not in href):
                    #logger.debug("regex match found")
                    reply_id_str = id_regex.group(1)
                    #logger.debug(f"{reply_id_str=}")
                    try:
                        reply_id = int(reply_id_str)
                    except ValueError:
                        continue
                    if reply_id != status_id:
                        new_nodes.append(reply_id)
                        if reply_id not in all_nodes:
                            all_nodes.append(reply_id)
            # if the new nodes were already found, we reached the end of the page
            #logger.debug(f"{new_nodes=}")
            #logger.debug(f"{all_nodes=}")
            #logger.debug(f"{counter=}")
            if not new_nodes and counter > 0:
                break
            if new_nodes == old_nodes and counter > 0:
                break
            old_nodes = new_nodes
            new_nodes.clear()
            # Scroll down to the bottom.
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            sleep(250, 500)
            counter += 1
        # reintegrate root status id so that it gets created in db if it doesn't
        # exist yet
        all_nodes.append(status_id)
        #logger.debug(f"returning: {all_nodes=}")
        return all_nodes

    def get_replies_of_status_list(self):
        batch = []
        for _id in self.sids:
            nodes = self.get_tree_nodes(_id)
            #logger.debug(f"{nodes=}")
            if nodes and type(nodes) is list:
                batch.extend(self.get_tree_nodes(_id))
        #logger.debug(f"return: {batch=}")
        return batch

    def clickShowReplies(self):
        self.driver.implicitly_wait(0)
        try:
            showReplies = self.driver.find_element_by_xpath("//div[text()='Show Replies']")
            if showReplies.isDisplayed():
                action = ActionChains(self.driver)  
                action.move_to_element(showReplies).click().perform()
        except NoSuchElementException:
            return
        finally:
            self.driver.implicitly_wait(1)
 

def record_replies(statusids, community):
    rc = ReplyCrawler(community, statusids)
    tree_id_lst = rc.get_replies_of_status_list()
    new_id_arr = np.setdiff1d(
        np.unique(np.array(tree_id_lst)),
        np.array(Tweetdj.objects.values_list("statusid", flat=True))
    )
    if new_id_arr.size == 0:
        return
    id_lst = list(new_id_arr)
    api = get_community_twitter_tweepy_api(community, backend=False)
    while id_lst:
        batch = id_lst[:98]
        del id_lst[0:98]
        statuses = api.statuses_lookup(batch, tweet_mode="extended")
        # sort statuses in reverse chronological order
        # so that the parents are added to the tree before their children
        statuses.sort(key=lambda x: x.id)
        for status in statuses:
            db = Addstatus(status._json)
            db.addtweetdj()
            in_reply_to_status_id = status._json["in_reply_to_status_id"]
            if in_reply_to_status_id:
                create_leaf(status._json["id"], in_reply_to_status_id)
            elif status._json["id"] in statusids:
                create_tree(status._json["id"])

def get_community_retweets(community_name: str) -> Optional[List[int]]:
    try:
        community = Community.objects.get(name=community_name)
    except Community.DoesNotExist:
        logger.error(
            'No Community named "%s" on this server.' % community_name
        )
        return
    su = get_community_bot_socialuser(community)
    if not su:
        return
    status_ids: List[int] = list(
        Tweetdj.objects.filter(retweeted_by=su).values_list(
            "statusid",
            flat=True
        )
    )
    return status_ids    
    
def lookup_replies(community_name, maximum=None):
    try:
        community = Community.objects.get(name=community_name)
    except:
        return
    status_id_list: List[int] = get_community_retweets(community_name)
    if maximum:
        status_id_list = status_id_list[0:maximum]
    rc = ReplyCrawler(community, status_id_list)
    rc.get_replies_of_status_list()
    
def get_replies(community_name, statusid):
    try:
        community = Community.objects.get(name=community_name)
    except:
        return
    rc = ReplyCrawler(community, [statusid])
    rc.get_replies_of_status_list()
    
def get_all_replies(community):
    roots_qs = Treedj.objects.all().order_by("-statusid")
    roots = roots_qs.values_list("statusid", flat=True)
    su = get_community_bot_socialuser(community)
    rt_by_ids = Tweetdj.objects.filter(
        retweeted_by=su,
        json__in_reply_to_status_id=None
    ).values_list("statusid", flat=True)
    for _id in rt_by_ids:
        if _id not in roots:
            create_tree(_id)
    roots = list(
        Treedj.objects
        .order_by("-statusid")
        .values_list("statusid", flat=True)
    )
    batch_size = 10
    batches = [roots[i:i + batch_size] for i in range(0, len(roots), batch_size)]
    for batch in batches:
        record_replies(batch, community)
        
def get_auth_driver_chrome(community):
        username = community.account.username
        password = community.account.password
        if not password or not username:
            return
        driver = getChromeRemoteDriver()
        if not driver:
            return
        driver.get("https://www.twitter.com/login")
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
        return driver