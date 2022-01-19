import logging

from hive.models import NotificationLog, NotificationService
from bot.tweepy_api import get_api
from tweepy.error import TweepError

logger = logging.getLogger(__name__)

def get_dm():
    try:
        return NotificationService.objects.get(name="dm")
    except NotificationService.DoesNotExist:
        return

def notify(statusid, json, socialuser, tweetsubscription, dct=None):
    for service in tweetsubscription.service.all().values_list("name", flat=True):
        if service == "dm":
            notify_dm(statusid, json, socialuser, tweetsubscription, dct=dct)
        
def notify_dm(
    statusid,
    json,
    socialuser,
    tweetsubscription,
    bot_screen_name="doctoctocbot2",
    dct=None,
    ):
    logger.debug(
       f"{statusid}, {socialuser}, {tweetsubscription}"    
    )
    api=get_api(username="doctoctocbot2", backend=True)
    try:
        screen_name = json["user"]["screen_name"]
    except:
        screen_name = bot_screen_name
    status_url = "https://twitter.com/{screen_name}/status/{status_id}".format(
        screen_name=screen_name,
        status_id=statusid,
    )
    try:
        status_text = json["full_text"]
    except KeyError:
        status_text = json["text"]
    except:
        status_text = ""
    # human readable category count dictionary
    rt_cat_count = {}
    for i in dct.keys():
        rt_cat_count[dct[i]["name"]]=dct[i]["count"]
    text = f"id: {tweetsubscription.id} " \
           f"lang: {[tli.tag for tli in tweetsubscription.language.all()]} " \
           f"cat: {[cat.name for cat in tweetsubscription.category.all()]} " \
           f"RT: {tweetsubscription.retweet_count} " \
           f"QT: {tweetsubscription.quote_count} \n" \
           f"{str(rt_cat_count)} \n" \
           f"{status_text} \n" \
           f"{status_url}"
    try:
        res = api.send_direct_message(
            recipient_id=socialuser.user_id,
            text=text
        )
        NotificationLog.objects.create(
            statusid=statusid,
            tweetsubscription=tweetsubscription,
            socialuser=socialuser,
            service=get_dm(),
            success=True,
            success_log=res._json
        )
    except TweepError as e:
        # if e.args[0][0]['code'] == 136:
        NotificationLog.objects.create(
            statusid=statusid,
            tweetsubscription=tweetsubscription,
            socialuser=socialuser,
            service=get_dm(),
            success=False,
            error_log=e.args[0][0]
        )