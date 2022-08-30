import sys, getopt
import string
import random
import logging
from time import sleep
from bot.tweepy_api import get_api

logger = logging.getLogger(__name__)

TEST_ACCOUNT = "cryptomed"

def randinterval():
    return random.randint(10, 30)/10 

def rnd_str_gen(size=15, chars= string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def get_test_api():
    return get_api(username=TEST_ACCOUNT)

def main(hashtag):
    api = get_test_api()
    if not api:
        return
    text = "[#{hashtag}] test ? [{rnd_str}]".format(hashtag=hashtag, rnd_str=rnd_str_gen())
    response = api.update_status(text)
    return response

if __name__ == '__main__':
    print("tweet test...")
    main(sys.argv[1:])