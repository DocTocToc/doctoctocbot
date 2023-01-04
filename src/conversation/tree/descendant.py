import logging
from typing import Optional
import queue
import threading
import sys
import pytz
from datetime import datetime, timedelta
import time
from bot.tweepy_api import get_api_2
from constance import config

from bot.lib.statusdb import Addstatus
from conversation.models import Treedj, Tweetdj
from conversation.models import create_leaf, create_tree
from community.helpers import get_community_twitter_tweepy_api
from community.models import Community
from bot.addstatusdj import addstatus
from conversation.tree.utils import get_community_roots
from mytweepy.errors import TweepyException

logger = logging.getLogger(__name__)

class ReplyCrawler(object):
    """
    A class used to represent an Twitter tree crawler based on the search API

    ...

    Attributes
    ----------
    community : Community
        a Community object, the crawler will build statuse trees of this community
    api : Tweepy API v1 object
        Tweepy API object
    api2 : Tweepy API v2 object
        Tweepy API v2 object
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
        self.api2= get_api_2(self.community.account.username)

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

    def get_replies(self, status_id, since_id=None):
        if not since_id:
            since_id = status_id
        replies = self.search_reply_to(
            status_id,
            since_id = since_id
        )
        logger.debug(f'{replies=}')
        if not replies:
            return
        logger.debug(
            f"{[(r.id, r.text, r.referenced_tweets) for r in replies]}"
        )
        if len(replies) == ReplyCrawler.max_count:
            while True:
                hi = 0
                for x in [reply.id for reply in replies]:
                    hi = max(x,hi)
                more_replies = self.search_reply_to(
                    status_id=status_id,
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
        logger.debug(f'{replies=}')
        if not replies:
            return
        root_descendants = ReplyCrawler.root_descendants(
            root.statusid,
            include_self=True
        )
        logger.debug(f"{root_descendants=}")
        # sort replies by id, by chronological order
        replies.sort(key = lambda i: i.id)
        logger.debug(f'sorted {replies=}')
        for r in replies:
            logger.debug(f'{r.text=}')
            logger.debug(f'{r.referenced_tweets=}')
            logger.debug(f"{root_descendants=}")
            for referenced_tweet in r.referenced_tweets:
                if referenced_tweet["type"] == "replied_to":
                    in_reply_to_status_id = referenced_tweet["id"]
                    logger.debug(f'{in_reply_to_status_id=}')
                    if in_reply_to_status_id in root_descendants:
                        create_leaf(r.id, in_reply_to_status_id)
                    break
        return root

    def build_tree(self, root_id):
        # Get existing descendants
        root_descendants_before = ReplyCrawler.root_descendants(
            root_id,
            include_self=True
        )
        self.add_leaves(root_id)

        root_descendants_after = ReplyCrawler.root_descendants(
            root_id,
            include_self=True
        )
        # Add new nodes to status database
        new_nodes = list(
            set(root_descendants_after) - set(root_descendants_before)
        )
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

    def search_reply_to(
            self,
            status_id: int,
            since_id: Optional[int] = None,
    
        ):
        """Return SearchObject list containing replies to screen_name
        Replies are limited to last 7 days.
        """
        status = self.api2.get_tweet(status_id, tweet_fields=['conversation_id', 'referenced_tweets'])
        logger.debug(f'{status=}')
        logger.debug(f'{status.data=}')
        logger.debug(f'{status.includes=}')
        try:
            conversation_id=int(status.data.conversation_id)
        except Exception as e:
            logger.error(e)
            return
        logger.debug(f'{conversation_id=}')
        q = f"conversation_id:{conversation_id}"
        try:
            response = self.api2.search_recent_tweets(
                q,
                since_id=since_id,
                #include_entities=True,
                max_results=ReplyCrawler.max_count,
                tweet_fields=['conversation_id', 'referenced_tweets'],
                expansions=['referenced_tweets.id']
            )
            logger.debug(f'{response=}')
            logger.debug(f'{response.data=}')
            logger.debug(f'{response.includes=}')
            return response.data
        except TweepyException as e:
            logger.error(e)

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
    # retry: number of seconds
    retry: int = community.tree_search_retry
    if not retry:
        retry = config.community__models__tree_search_retry__default
    retry_timedelta = timedelta(seconds=retry)
    elapsed: timedelta = stop_dt - start_dt
    if elapsed < retry_timedelta:
        sleep: int = (retry_timedelta - elapsed).total_seconds()
        logger.debug(
            f"Time elapsed since lat execution time inferior to 'retry': "
            f"sleeping for {sleep} seconds."
        )
        time.sleep(sleep)
    return True