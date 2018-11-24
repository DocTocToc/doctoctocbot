from django.core.management.base import BaseCommand, CommandError
from os import listdir
import os
from os.path import isfile, join, stat
import json
import tweepy
from bot.twitter import getAuth                                                     
from bot.conf.cfg import getConfig                                                  
from bot.log.log import setup_logging
import logging
from bot.lib.statusdb import Addstatus

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Add status to database from files'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        statusid_lst = []
        path = options['path']
        files = [f for f in listdir(path) if isfile(join(path, f))]
        for file in files:
            with open(join(path, file), 'r') as f:
                #jsn = json.loads(f.read())
                id_str = os.path.basename(f.name)
                #logger.debug(json.dumps(jsn))
                statusid_lst.append(int(id_str))
        
        size = len(statusid_lst)
        while size > 0:
            ids = statusid_lst[:100]
            del statusid_lst[:100]
            size -= 100
            API = tweepy.API(getAuth())
            #idstr = " ,".join( str(sid) for sid in ids )
            logger.debug(ids)
            status_lst = API.statuses_lookup(ids, include_entities=True, tweet_mode='extended')
            for status in status_lst:
                db = Addstatus(status._json)
                db.addtweetdj()
                self.stdout.write(self.style.SUCCESS('Successfully added status "%s" to database' % status._json["id"]))
        