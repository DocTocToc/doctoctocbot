import logging
import tweepy
from typing import Optional
from tweepy.streaming import StreamListener
from bot.tweepy_api import get_api
from bot.tasks import handle_on_status
from bot.lib.status import status_json_log
from community.models import Community
from bot.bin.search import retweet_recent

logger = logging.getLogger(__name__)

class StdOutListener(StreamListener):

    def on_status(self, status):
        logger.info(f'on_status: {status_json_log(status._json)}')
        handle_on_status.apply_async(
            kwargs={"json": status._json, "community": self.community},
            ignore_result=True
        )
        return True

    def on_error(self, status_code):
        logger.error(status_code)
        if status_code == 420:
            return False
        if status_code == 401:
            logger.error(
                "401 Unauthorized "
                "Missing or incorrect authentication credentials. "
                "This may also returned in other undefined circumstances."
            )
            return False

class CommunityStdOutListener(StdOutListener):

    def __init__(self, community: str, **kwds):
        self.community = community
        super().__init__(**kwds)


def main(community: Optional[str] = None):
    if not community:
        return
    try:
        community_mi = Community.objects.get(name=community)
    except Community.DoesNotExist:
        return
    try:
        screen_name = community_mi.account.username
    except:
        return
    try:
        api = get_api(username=screen_name)
    except:
        return
    track_list = []
    try:
        hashtags = Community.objects.get(name=community).hashtag.all()
    except Community.DoesNotExist:
        return
    if not hashtags:
        return
    for hashtag in hashtags:
        track_list.append(f"#{hashtag}")
    # search for and process recent tweets containing this community's hashtags
    retweet_recent(track_list, community, api)
    # start stream listener
    l = CommunityStdOutListener(community=community)
    try:
        stream = tweepy.Stream(auth = api.auth, listener=l)
    except AttributeError as e:
        logger.error(f"{e}")
        return
    stream.filter(track = track_list)

if __name__ == '__main__':
    main()
