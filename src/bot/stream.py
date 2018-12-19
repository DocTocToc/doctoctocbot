from tweepy.streaming import StreamListener
from tweepy import Stream
import tweepy
import json
from bot.conf.cfg import getConfig
from bot.twitter import getAuth
from bot.log.log import setup_logging
import logging
from .tasks import handle_on_status

setup_logging()
logger = logging.getLogger(__name__)

config = getConfig()

#import pkgutil
#search_path = '.' # set to None to see all modules importable from sys.path
#all_modules = [x[1] for x in pkgutil.iter_modules(path=search_path)]
#print(all_modules)

def printStatus( status ):
    "output stuff"
    json_str = json.dumps(status._json)
    print(json_str)
    print("\n")
    return

#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):

    def on_status(self, status):
        #logger.debug("stream status: %s", status._jsonj)
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
    hashtags = config["keyword_track_list"]
    for hashtag in hashtags:
        track_list.append(hashtag)
    stream.filter(track = track_list)

if __name__ == '__main__':
    main()