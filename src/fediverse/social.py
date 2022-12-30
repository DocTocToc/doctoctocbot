import logging
from moderation.models import MastodonUser, MastodonFollower, MastodonFriend
from fediverse.api import get_mastodon_api
from fediverse.models import MastodonAccess
from django.db import DatabaseError

logger = logging.getLogger(__name__)

def user_local_id(user: MastodonUser, access: MastodonAccess):
    if user.local_id:
        return user.local_id
    mastodon = get_mastodon_api(access.user.acct, access.app.client_name)
    q=f'@{user.acct}'
    s=mastodon.search_v2(q=q, exclude_unreviewed=False)
    accounts = s["accounts"]
    try:
        local_id=accounts[0]['id']
    except:
        logger.error(f"Account {user} not found on local server")
    user.local_id=local_id
    user.save()
    return local_id

def record_followers(user: MastodonUser, access: MastodonAccess):
    mastodon = get_mastodon_api(user.acct, access.app.client_name)
    if not user.local_id:
        local_id=user_local_id(user, access)
    else:
        local_id=user.local_id
    followers = mastodon.account_followers(id = local_id)
    followers = mastodon.fetch_remaining(followers)
    ids = [follower["id"] for follower in followers]
    try:
        MastodonFollower.objects.create(
            user=user,
            id_list=ids
        )
    except DatabaseError as e:
        logger.error(e)
        return

def record_friends(user: MastodonUser, access: MastodonAccess):
    mastodon = get_mastodon_api(user.acct, access.app.client_name)
    if not user.local_id:
        local_id=user_local_id(user, access)
    else:
        local_id=user.local_id
    friends = mastodon.account_following(id = local_id)
    friends = mastodon.fetch_remaining(friends)
    ids = [friend["id"] for friend in friends]
    try:
        MastodonFriend.objects.create(
            user=user,
            id_list=ids
        )
    except DatabaseError as e:
        logger.error(e)
        return