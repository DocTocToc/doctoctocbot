import logging
from community.models import Community, Reblog
from moderation.models import MastodonUser, MastodonFollower, MastodonFriend
from fediverse.models import Toot
from fediverse.api import get_mastodon_api
from fediverse.social import record_followers, record_friends, user_local_id

logger = logging.getLogger(__name__)


class TootProcessor:
    def __init__(self, pk: int, community: Community) -> None:
        try:
            self.toot = Toot.objects.get(pk=pk)
        except Toot.DoesNotExist as e:
            logger.error(e)
            return
        self.hashtags = self.toot.hashtag.all()
        self.community = community
        self.bot: MastodonUser = community.mastodon_account
        self.api = self.get_api()

    def triage(self):
        if not self.has_reblog_hashtag():
            msg = f"{self.toot} has no reblog hashtag ({self.hashtags})"
            logger.info(msg)
            return msg

        if Reblog.objects.filter(
            community=self.community,
            hashtag__in=self.hashtags,
            require_follower=True
        ).exists() and not self.is_follower():
            msg = f"No reblog: {self.toot.user} does not follow {self.bot}"
            logger.info(msg)
            return msg

        if Reblog.objects.filter(
            community=self.community,
            hashtag__in=self.hashtags,
            require_following=True
        ).exists() and not self.is_friend():
            msg = f"No reblog: {self.toot.user} is not a friend of {self.bot}"
            logger.info(msg)
            return msg
        return self.reblog()

    def reblog(self):
        logger.info(f'Reblogging toot {self.toot.db_id}')
        res = self.api.status_reblog(self.toot.db_id, "private")
        logger.info(f'Reblogged: {res}')

    def is_follower(self):
        record_followers(self.bot, self.community.mastodon_access)
        try:
            bot_followers = MastodonFollower.objects.filter(
                user=self.bot).latest().id_list
        except MastodonFollower.DoesNotExist as e:
            logger.error(e)
            return False
        local_id=user_local_id(self.toot.user, self.community.mastodon_access)
        return local_id in bot_followers

    def is_friend(self):
        record_friends(self.bot, self.community.mastodon_access)
        try:
            bot_friends = MastodonFriend.objects.filter(
                user=self.bot).latest().id_list
        except MastodonFriend.DoesNotExist as e:
            logger.error(e)
            return False
        return self.toot.user.local_id in bot_friends

    def get_api(self):
        return get_mastodon_api(
            acct=self.community.mastodon_account.acct,
            client_name=self.community.mastodon_access.app.client_name
        )

    def has_reblog_hashtag(self):
        reblog_hashtags = [r.hashtag for r in Reblog.objects.filter(
            community=self.community,
            reblog=True
        )]
        return not set(self.hashtags).isdisjoint(set(reblog_hashtags))
