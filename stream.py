#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
#from tweepy import OAuthHandler
from tweepy import Stream
import json
from conf.cfg import getConfig
from twitter import getAuth
from doctoctocbot import okrt, retweet
from log import setup_logging
import logging
from lib.statusdb import addstatus

setup_logging()
logger = logging.getLogger(__name__)

config = getConfig()

def printStatus( status ):
    "output stuff"
    json_str = json.dumps(status._json)
    print(json_str)
    print("\n")
    return

#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):

    def on_status(self, status):
        logger.debug(status._json)
        logger.debug("is this status ok for RT? %s" , str(okrt(status._json)))
        if okrt(status._json):
            logger.info("retweeting status %s: %s ", status.id, status.text)
            retweet(status.id)
        dbstatus = addstatus(status._json)
        dbstatus.addstatus()
        return True

    def on_error(self, status_code):
            logger.error(status_code)
            if status_code == 420:
                return False


if __name__ == '__main__':

    #This handles Twitter authentication and the connection to Twitter Streaming API
    l = StdOutListener()
    auth = getAuth()
    stream = Stream(auth, l)

    #This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
    search = []
    search.append(config['settings']['search_query'])
    logger.info(search)
    stream.filter(track = ["#doctoctoctest"])
