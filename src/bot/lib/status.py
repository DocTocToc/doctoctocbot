import logging
from typing import Optional
from bot.tweepy_api import get_api
from bot.models import Account
from tweepy.error import TweepError

logger = logging.getLogger(__name__)

def status_json_log(_json):
    try:
        hashtags = [ h['text'] for h in _json['entities']['hashtags'] ]
    except Exception as e:
        logger.error(e)
        return
    return (
        f"id: {_json['id']}\n"
        f"created_at: {_json['created_at']}\n"
        f"screen_name: {_json['user']['screen_name']}\n"
        f"text: {_json['text']}\n"
        f"retweeted_status: {'retweeted_status' in _json}"
        f"hashtags: {hashtags}"
    )

def api_switch_get_status(
        statusid: int,
        tweet_mode: Optional[str] = 'extended',
        exclude: Optional[str] = None
    ):
    """Try all available Twitter accounts to get a status.
    This function allows us to bypass unprotected accounts who blocked one
    of our accounts but not all of them.
    """
    for username in (
        Account.objects
        .exclude(username=exclude)
        .values_list("username", flat=True)
        ):
        api = get_api(username=username)
        try:
            return api.get_status(statusid, tweet_mode=tweet_mode)
        except TweepError as e:
            logger.error(f"{e}")
            continue