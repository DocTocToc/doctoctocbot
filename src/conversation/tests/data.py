from datetime import datetime
import logging
import pytz

from conversation.models import Tweetdj


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def userhashtagcount_db(data):
    for d in data:
        dt_str = d["created_at"]
        dt = datetime.strptime(dt_str, "%a %b %d %H:%M:%S %z %Y")

        Tweetdj.objects.create(statusid = d["statusid"],
                               userid = d["userid"],
                               json = d["json"],
                               created_at = dt,
                               reply = d["reply"],
                               like = d["like"], 
                               retweet = d["retweet"],
                               parentid = d["parentid"],
                               hashtag0 = d["hashtag0"],
                               hashtag1 = d["hashtag1"],
                               quotedstatus = d["quotedstatus"],
                               retweetedstatus = d["retweetedstatus"],
                               deleted = d["deleted"] 
                               )