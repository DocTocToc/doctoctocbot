import logging
import tweepy
from tweepy.streaming import StreamListener

from django.conf import settings
from bot.twitter import getAuth

from .tasks import handle_on_status
from bot.lib.status import status_json_log

logger = logging.getLogger(__name__)

class StdOutListener(StreamListener):

    def on_status(self, status):
        logger.info("%s", status_json_log(status._json))
        handle_on_status.apply_async(args=(status.id,))
        return True

    def on_error(self, status_code):
        logger.error(status_code)
        if status_code == 420:
            return False

def main():
    #This handles Twitter authentication and the connection to Twitter Streaming API
    l = StdOutListener()
    stream = tweepy.Stream(getAuth(), l)
    #This line filter Twitter Streams to capture data by the keywords
    track_list = []
    hashtags = settings.KEYWORD_TRACK_LIST
    for hashtag in hashtags:
        track_list.append(hashtag)
    stream.filter(track = track_list)

if __name__ == '__main__':
    main()