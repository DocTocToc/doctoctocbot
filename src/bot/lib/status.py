import logging
from typing import Optional
from bot.tweepy_api import get_api
from bot.models import Account
from tweepy.error import TweepError

logger = logging.getLogger(__name__)

def status_json_log(json):
    return (
        f"Id: {json['id']}; "
        f"Created_at: {json['created_at']}; "
        f"Screen_name: {json['user']['screen_name']}; "
        f"Text: {json['text']} \n"
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