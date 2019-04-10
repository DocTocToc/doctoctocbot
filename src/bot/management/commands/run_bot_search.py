from django.core.management.base import  BaseCommand, CommandError
from django.conf import settings
from bot.doctoctocbot import isauthorized, isrt, isquestion, okrt
import hashlib
import os
import tweepy
from bot.twitter import getAuth
import logging

class Command(BaseCommand):
    help = 'Run bot search and retweet'
    
    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        # build savepoint path + file
        keyword_list = settings.KEYWORD_RETWEET_LIST
        search_string = " OR ".join(keyword_list)
        search_string = search_string + u" -filter:retweets"
        logger.debug("search_string: %s" % (search_string))
        hashedHashtag = hashlib.sha256(search_string.encode('ascii')).hexdigest()
        last_id_filename = "last_id_hashtag_%s" % hashedHashtag
        rt_bot_path = os.path.dirname(os.path.abspath(__file__))
        last_id_file = os.path.join(rt_bot_path, last_id_filename)
        
        # create bot
        api = tweepy.API(getAuth())
        
        # retrieve last savepoint if available
        try:
            with open(last_id_file, "r") as f:
                savepoint = f.read()
        except IOError:
            savepoint = ""
            logger.debug("No savepoint found. Bot is now searching for results")
        
        
        # Tweet language (empty = all languages)
        tweetLanguage = settings.TWEET_LANGUAGE
        
        # search query
        timelineIterator = tweepy.Cursor(
            api.search,
            q=search_string,
            since_id=savepoint,
            lang=tweetLanguage,
            tweet_mode='extended'
        ).items(settings.NUMBER_OF_RT)
        
        # put everything into a list to be able to sort/filter        
        oklist = []
        
        for tweet in timelineIterator:
            status = api.get_status(tweet.id,  tweet_mode='extended')
            status_json = status._json
            user = tweet.user
            screenname = user.screen_name
            userid = user.id
            useridstring = str(userid)
            logger.debug("userid: %s", userid)
            logger.debug("useridstring: %s", useridstring)
            logger.debug("screen name: %s", screenname)
            logger.debug("text: %s", tweet.full_text.encode('utf-8'))
            logger.debug("Is user authorized? %s", isauthorized(status_json))
            logger.debug("isrt: %s", isrt(status_json))
            logger.debug("status 'retweeted': %s", status_json['retweeted'])
            logger.debug("is this a question? %s", isquestion(status_json))
            if okrt(status_json):
                oklist.append(tweet)
                logger.debug(":) OK for RT")
            else:
                logger.debug(":( not ok for RT")
        
        try:
            last_tweet_id = oklist[0].id
        except IndexError:
            last_tweet_id = savepoint
        
        # filter bad words & users out and reverse timeline
        wordbadlist = set((u"remplacant",u"RT",u"remplaçant"))
        oklist = filter(lambda tweet: not any(word in tweet.full_text.split() for word in wordbadlist), oklist)
        
        oklist = list(oklist)
        oklist.reverse()
        
        tw_counter = 0
        err_counter = 0
        
        # iterate the timeline and retweet
        for status in oklist:
            try:
                logger.debug("(%(date)s) %(name)s: %(message)s\n" % \
                      {"date": status.created_at,
                       "name": status.author.screen_name.encode('utf-8'),
                       "message": status.full_text.encode('utf-8')})
        
                api.retweet(status.id)
                tw_counter += 1
            except tweepy.error.TweepError as e:
                # just in case tweet got deleted in the meantime or already retweeted
                err_counter += 1
                logger.debug("error: %s", e)
                continue
        
        logger.info("Finished. %d Tweets retweeted, %d errors occured." % (tw_counter, err_counter))
        
        # write last retweeted tweet id to file
        with open(last_id_file, "w") as f:
            f.write(str(last_tweet_id))
        
        self.stdout.write(self.style.SUCCESS('Done searching & retweeting.'))