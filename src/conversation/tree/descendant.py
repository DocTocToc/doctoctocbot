import logging
from typing import Optional
import queue
import threading
import sys
import pytz
from datetime import datetime, timedelta
import time

from constance import config

from bot.lib.statusdb import Addstatus
from conversation.models import Treedj, Tweetdj
from conversation.models import create_leaf, create_tree
from community.helpers import get_community_twitter_tweepy_api
from community.models import Community
from bot.addstatusdj import addstatus
from conversation.tree.utils import get_community_roots

logger = logging.getLogger(__name__)

class ReplyCrawler(object):
    """
    A class used to represent an Twitter tree crawler based on the search API

    ...

    Attributes
    ----------
    community : Community
        a Community object, the crawler will build statuse trees of this community
    api : Tweepy API object
        Tweepy API object
    root_id : int
        status id of the root of the tree
    q : PriorityQueue
        unused
    since_id: int
        search will start from this id
    tree_init: List[int]
        list of ids of descendants already known for this tree root

    Methods
    -------
    TODO

    """
    max_count = 100
    
    def __init__(self, community):
        self.community = community
        self.api = get_community_twitter_tweepy_api(self.community)
        #self.root_id = root_id
        #self.q = queue.PriorityQueue(maxsize=0)
        #self.since_id = root_id
        #self.tree_init = ReplyCrawler.root_descendants(
        #    root_id,
        #    include_self=True
        #)

    @staticmethod
    def root_descendants(root_id, include_self: bool = True):
        """Return list of descendants' ids
        """
        try:
            root = Treedj.objects.get(statusid=root_id)
        except Treedj.DoesNotExist:
            root = create_tree(root_id)
        if root:
            return sorted( 
                list(
                    root.get_descendants(include_self=include_self)
                    .values_list("statusid", flat=True)
                )
            )

    def get_screen_name(self, status_id):
        try:
            status = Tweetdj.objects.get(statusid=status_id)
            return status.json["user"]["screen_name"]
        except Tweetdj.DoesNotExist:
            logger.debug(f"Tweet {status_id} is not present in database.")
            addstatus(status_id, bot_username=self.community.account.username)
            if Tweetdj.objects.filter(statusid=status_id).exists():
                return self.get_screen_name(status_id)
        except TypeError:
            if status.json is None:
                logger.debug(f"Tweet {status_id} json field is null.")
            return
        except KeyError:
            logger.debug(f"Tweet {status_id} json is buggy.")
            return

    def get_replies(self, status_id, since_id=None):
        screen_name = self.get_screen_name(status_id)
        if not since_id:
            since_id = status_id
        replies = self.search_reply_to(
            screen_name,
            community=self.community,
            since_id = since_id
        )
        logger.debug(f"{[(r.id, r.text) for r in replies]}")
        if len(replies) == ReplyCrawler.max_count:
            while True:
                hi = 0
                for x in [reply.id for reply in replies]:
                    hi = max(x,hi)
                more_replies = self.search_reply_to(
                    screen_name,
                    community=self.community,
                    since_id = hi
                )
                if more_replies:
                    replies.extend(more_replies)
                if len(more_replies) < 100:
                    break
                replies = more_replies
        return replies

    def add_leaves(self, root_id):
        try:
            root = Treedj.objects.get(statusid=root_id)
        except Treedj.DoesNotExist:
            return
        replies = self.get_replies(root_id, since_id=root_id)
        if not replies:
            return
        root_descendants = ReplyCrawler.root_descendants(
            root.statusid,
            include_self=True
        )
        logger.debug(f"{root_descendants=}")
        # sort replies by id, by chronological order
        replies.sort(key = lambda i: i.id)
        for r in replies:
            if r.in_reply_to_status_id in root_descendants:
                create_leaf(r.id, r.in_reply_to_status_id)
        return root

    def build_tree(self, root_id):
        root = self.add_leaves(root_id)
        if not root:
            return
        # Get existing descendants
        root_descendants = ReplyCrawler.root_descendants(
            root.statusid,
            include_self=True
        )
        # Search for new leaves
        for r in root_descendants:
            self.add_leaves(r)
        tree_current = ReplyCrawler.root_descendants(
            root_id,
            include_self=True
        )
        # Add new nodes to status database
        new_nodes = list(set(tree_current) - set(root_descendants))
        if new_nodes:
            self.lookup_status(new_nodes)

    def lookup_status(self, ids):
        def paginator(seq, rowlen):
            for start in range(0, len(seq), rowlen):
                yield seq[start:start+rowlen]
        for _ids in paginator(ids, 99):
            statuses = self.api.statuses_lookup(_ids, tweet_mode="extended")
            for status in statuses:
                db = Addstatus(status._json)
                db.addtweetdj()

    """
    def enqueue_nodes(self, replies):
        for reply in replies:
            self.q.put(reply.id)
    """

    def search_reply_to(
            self,
            screen_name: str,
            community: Community,
            since_id: Optional[int] = None,
    
        ):
        """Return SearchObject list containing replies to screen_name
        Replies are limited to last 7 days.
        """
        q = f"@{screen_name}"
        try:
            return self.api.search(
                q=q,
                since_id=since_id,
                include_entities=True,
                count=ReplyCrawler.max_count
            )
        except AttributeError:
            logger.error("Probable Tweepy API error.")


def tree_search_crawl(
        community_name,
        days: int = (
            config.conversation__tree__descendant__tree_search_crawl__days
        )
    ):
    try:
        community = Community.objects.get(name=community_name)
    except Community.DoesNotExist:
        return False
    # get tree roots for this community created less than 7 days ago
    lower_dt = datetime.utcnow().replace(tzinfo=pytz.utc) - timedelta(days=days)
    logger.debug(f"{lower_dt=}")
    roots = get_community_roots(community, lower_dt=lower_dt)
    if not roots:
        backoff = community.no_root_backoff
        if not backoff:
            backoff = config.community__models__no_root_backoff__default
        logger.debug(f"No root found. Sleeping for {backoff} seconds.")
        time.sleep(backoff)
        return True
    rc = ReplyCrawler(community)
    start_dt = datetime.utcnow()
    logger.info(
        f"Starting tree_search_crawl loop over {len(roots)} root nodes "
        f"at {start_dt} UTC."
    )
    for root in roots:
        rc.build_tree(root)
    stop_dt = datetime.utcnow()
    logger.info(
        f"Ending tree_search_crawl loop over {len(roots)} root nodes "
        f"at {stop_dt} UTC. \n"
        f"(Loop had started at {start_dt} UTC.)"
    )
    retry = community.tree_search_retry
    if not retry:
        retry = config.community__models__tree_search_retry__default
    diff = retry - (stop_dt - start_dt)
    if diff > 0:
        logger.debug(
            f"Execution time inferior to retry minimum. "
            f"Sleeping for {backoff} seconds."
        )
        time.sleep(diff)
    return True