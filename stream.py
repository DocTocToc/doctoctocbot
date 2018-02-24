#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import os, configparser, inspect, json
from doctoctocbot import okrt, retweet
from log import setup_logging
import logging

setup_logging()

logger = logging.getLogger(__name__)
path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
config = "configtest"                                                           
#config = "config_prod"
configfile = os.path.join(path, config)         
config = configparser.SafeConfigParser()                                        
config.read(configfile)

def printStatus( status ):
    "output stuff"
    json_str = json.dumps(status._json)
    print(json_str)
    print("\n")
    return


#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):

    def on_status(self, status):
            if okrt(status._json):
                logger.info("retweeting status %s: %s ", status.id, status.text)
                retweet(status.id)
            return True

    def on_error(self, status_code):
            logger.error(status)
            if status_code == 420:
                return False


if __name__ == '__main__':

    #This handles Twitter authetification and the connection to Twitter Streaming API
    l = StdOutListener()
    auth = OAuthHandler(config.get("twitter", "consumer_key"), config.get("twitter", "consumer_secret"))
    auth.set_access_token(config.get("twitter", "access_token"), config.get("twitter", "access_token_secret"))
    stream = Stream(auth, l)

    #This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
    stream.filter(track=['#doctoctoctest'])
