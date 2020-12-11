import logging
import tweepy
from tweepy.streaming import StreamListener
from bot.tweepy_api import get_api
from conversation.models import Hashtag, Tweetdj
from bot.tasks import handle_on_status
from bot.lib.status import status_json_log
from community.models import Community
from bot.bin.search import retweet_recent

logger = logging.getLogger(__name__)

class StdOutListener(StreamListener):

    def on_status(self, status):
        logger.info("%s", status_json_log(status._json))
        handle_on_status.apply_async(args=(status._json,), ignore_result=True)
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

def main(community=None):
    if not community:
        return
    #This handles Twitter authentication and the connection to Twitter Streaming API
    try:
        screen_name = Community.objects.get(name=community).account.username
    except:
        screen_name = None
    api = get_api(screen_name, backend=True)
    l = StdOutListener()
    try:
        stream = tweepy.Stream(auth = api.auth, listener=l)
    except AttributeError as e:
        logger.error(f"{e}")
        return
    #This line filter Twitter Streams to capture data by the keywords
    track_list = []
    try:
        hashtags = Community.objects.get(name=community).hashtag.all()
    except Community.DoesNotExist:
        return
    if not hashtags:
        return
    for hashtag in hashtags:
        track_list.append(f"#{hashtag}")
    stream.filter(track = track_list)
    # search for tweets containing the hashtags sent while server was down
    retweet_recent(track_list, api)

if __name__ == '__main__':
    main()
