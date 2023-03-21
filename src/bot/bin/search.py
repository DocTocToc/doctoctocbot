import logging
from conversation.models import Tweetdj
from bot.tasks import handle_on_status
from community.models import Community

logger = logging.getLogger(__name__)

def retweet_recent(track_list: list[str], community: str, api):
    logger.debug(
        f'retweet_recent({track_list=}, {community=}, {api=})'
    )
    search_results = api.search(
        q=" OR ".join(track_list),
        result_type="recent"
    )
    logger.info(f"Found {len(search_results)=} tweets.")
    if not len(search_results):
        return
    try:
        community_mi = Community.objects.get(name=community)
    except Community.DoesNotExist as e:
        logger.error(e)
        return
    try:
        bot_userid=community_mi.account.socialuser.user_id
    except:
        logger.error(f'No SocialUser associated with {community_mi}')
        return
    for status in search_results:
        if not Tweetdj.objects.filter(
            userid=bot_userid,
            json__retweeted_status__id=status.id
        ).exists():
            logger.debug(f"create handle_on_status task for {status._json=}")
            handle_on_status.apply_async(
                args=(status._json, community),
                ignore_result=True
            )

 