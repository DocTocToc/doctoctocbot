import os
import tweepy
import json
import yaml
import logging
import concurrent.futures
from datetime import timedelta, datetime

from bot.tweepy_api import get_api

logger = logging.getLogger(__name__)


class TwitterWipe():

    def __init__(self, username, favorites=0, retweets=0, tweets=0):
        self.username = username
        self.favorites = favorites
        self.retweets = retweets
        self.tweets = tweets
        self.delete_timestamps = self.get_delete_timestamps()
        self.api = get_api(username=self.username)

    def confirm(self, default=None):
        result = input(
            "Are you sure that you want to wipe the Twitter account @%s? "
            "This cannot be undone! Please answer 'yes' or 'no'.\n>"
            % self.username
        )
        if not result and default is not None:
            return default
        while result.lower() not in ["yes", "no"]:
            result = input("Please answer 'yes' or 'no': ")
        return result.lower() == "yes"

    def run(self):
        logger.info('starting twitterwipe')
        if not self.api:
            logger.error('Twitter API not valid')
            return
        if not self.confirm(default=False):
            return
        self.purge_activity()
        logger.info('done')

    def get_delete_timestamps(self):
        curr_dt_utc = datetime.utcnow()
        favorites_time = None
        retweets_time = None
        tweets_time = None
        if self.favorites >= 0:
            favorites_delta = timedelta(days=self.favorites)
            favorites_time = curr_dt_utc - favorites_delta
        else:
            favorites_time = datetime.min
        if self.retweets >= 0:
            retweets_delta = timedelta(days=self.retweets)
            retweets_time = curr_dt_utc - retweets_delta
        else:
            retweets_time = datetime.min
        if self.tweets >=0:
            tweets_delta = timedelta(days=self.tweets)
            tweets_time = curr_dt_utc - tweets_delta
        else:
            tweets_time = datetime.min
        return (favorites_time, retweets_time, tweets_time)

    def purge_activity(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as e:
            e.submit(self.delete_tweets, self.delete_timestamps[2])
            e.submit(self.delete_retweets, self.delete_timestamps[1])
            e.submit(self.delete_favorites, self.delete_timestamps[0])

    def delete_tweets(self, ts):
        logger.info('deleting tweets before {}'.format(str(ts)))
        count = 0
        for status in tweepy.Cursor(self.api.user_timeline).items():
            if status.created_at < ts:
                try:
                    self.api.destroy_status(status.id)
                    count += 1
                except Exception as e:
                    logger.error(
                        "failed to delete {}".format(status.id),
                        exc_info=True
                    )
        logger.info('{} tweets deleted'.format(count))
        return

    def delete_retweets(self, ts):
        logger.info('deleting retweets before {}'.format(str(ts)))
        count = 0
        for status in tweepy.Cursor(self.api.user_timeline).items():
            if status.created_at < ts:
                try:
                    self.api.unretweet(status.id)
                    count+=1
                except:
                    logger.error(
                        'failed to unretweet {}'.format(status.id),
                        exc_info=True
                    )
        logger.info('{} retweets deleted'.format(count))   
        return

    def delete_favorites(self, ts):
        logger.info('deleting favorites before {}'.format(str(ts)))
        count = 0
        for status in tweepy.Cursor(self.api.favorites).items():
            if status.created_at < ts:
                try:
                    self.api.destroy_favorite(status.id)
                    count+=1
                except:
                    logger.error(
                        'failed to delete favorite'.format(status.id),
                        exc_info=True
                    )
        logger.info('{} favorites deleted'.format(count))
        return