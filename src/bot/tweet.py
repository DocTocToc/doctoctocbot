"""
Tweet object utilities
"""

from typing import List

def hashtag_list(status) -> List:
    if 'extended_tweet' in status:
        status = status['extended_tweet']
    #logger.debug("status in has_retweet_hashtag: %s", status)
    return [hashtag["text"].lower() for hashtag in status["entities"]["hashtags"]]