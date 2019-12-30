import logging
import tweepy
from tweepy.streaming import StreamListener

from bot.tweepy_api import getAuth
from conversation.models import Hashtag
from bot.tasks import handle_on_status
from bot.lib.status import status_json_log
from community.models import Community

logger = logging.getLogger(__name__)

class StdOutListener(StreamListener):

    def on_status(self, status):
        logger.info("%s", status_json_log(status._json))
        handle_on_status.apply_async(args=(status.id,), ignore_result=True)
        return True

    def on_error(self, status_code):
        logger.error(status_code)
        if status_code == 420:
            return False

def main(community=None):
    #This handles Twitter authentication and the connection to Twitter Streaming API
    try:
        screen_name = Community.objects.get(name=community).account.username
    except:
        screen_name = None
    auth = getAuth(screen_name)
    l = StdOutListener()
    stream = tweepy.Stream(auth, l)
    #This line filter Twitter Streams to capture data by the keywords
    track_list = []
    if community is None:
        hashtags = Hashtag.objects.values_list("hashtag", flat=True)
    else:
        try:
            hashtags = Community.objects.get(name=community).hashtag.all()
        except Community.DoesNotExist:
            hashtags = Hashtag.objects.values_list("hashtag", flat=True)
    for hashtag in hashtags:
        track_list.append(f"#{hashtag}")
    stream.filter(track = track_list)

if __name__ == '__main__':
    main()