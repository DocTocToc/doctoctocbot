import logging
from conversation.models import Tweetdj
from bot.tasks import handle_on_status

logger = logging.getLogger(__name__)

def retweet_recent(track_list: str, community: str, api):
    logger.debug(
        f'retweet_recent({track_list=}, {community=}, {api=})'
    )
    search_results = api.search(
        q=" OR ".join(track_list),
        result_type="recent"
    )
    logger.debug(f"{len(search_results)=}")
    for status in search_results:
        if not Tweetdj.objects.filter(statusid=status.id).exists():
            logger.debug(f"{status._json=}")
            handle_on_status.apply_async(
                args=(status._json, community),
                ignore_result=True
            )
