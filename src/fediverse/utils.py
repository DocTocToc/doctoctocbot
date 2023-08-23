from fediverse.models import Toot
from community.models import Community
from fediverse.api import get_mastodon_api
from  fediverse.bot import TootProcessor
import logging

logger = logging.getLogger(__name__)

def triage(pk, community):
    try:
        community = Community.objects.get(name=community)
    except Community.DoesNotExist:
        return
    tp=TootProcessor(pk, community)
    res = tp.triage()
    logger.debug(res)

def warn(pk:int, community):
    try:
        toot=Toot.objects.get(id=pk)
    except Toot.DoesNotExist:
        return
    try:
        community = Community.objects.get(name=community)
    except Community.DoesNotExist:
        return
    mentions = []
    entities = community.admins.all()
    for entity in entities:
        for mastodonuser in entity.mastodonuser_set.all():
            mentions.append(mastodonuser)
    if not mentions:
        return
    mentions_str = " ".join(
        [f'@{mention.acct}' for mention in mentions]
    )
    hashtag_str = " ".join(
        [f'# {hashtag.hashtag}' for hashtag in toot.hashtag.all()]
    )
    url_str = toot.status["url"]
    toot_str = " ".join([mentions_str, hashtag_str, url_str])
    logger.debug(toot_str)
    mastodon = get_mastodon_api(
        acct=community.mastodon_access.user.acct,
        client_name=community.mastodon_access.app.client_name
    )
    mastodon.status_post(toot_str, visibility='direct')