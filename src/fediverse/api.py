import logging
from mastodon import Mastodon, MastodonError
from moderation.models import MastodonUser
from fediverse.models import MastodonApp, MastodonAccess

logger = logging.getLogger(__name__)

def get_mastodon_api(acct: str, client_name: str) -> Mastodon:
    try:
        user=MastodonUser.objects.get(acct=acct)
    except MastodonUser.DoesNotExist as e:
        logger.error(e)
        return
    try:
        app = MastodonApp.objects.get(client_name=client_name)
    except MastodonApp.DoesNotExist as e:
        logger.error(e)
        return
    try:
        access = MastodonAccess.objects.get(user=user, app=app)
    except MastodonAccess.DoesNotExist as e:
        logger.error(e)
    try:
        return Mastodon(
            access_token=access.access_token,
            api_base_url=access.app.api_base_url
        )
    except MastodonError as e:
        logger.error(e)