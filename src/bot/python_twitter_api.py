import twitter

from social_django.models import UserSocialAuth
from django.contrib.auth import get_user_model

from bot.models import Account


def get_api(username=None):
    "get Python-Twitter API object"
    if username:
        try:
            account = Account.objects.get(username=username)
        except Account.DoesNotExist:
            return getSocialDjangoAuth(username)
        api = twitter.API(
            consumer_key = account.twitter_consumer_key,
            consumer_secret = account.twitter_consumer_secret,
            access_token_key = account.twitter_access_token,
            access_token_secret = account.twitter_access_token_secret
        )
    else:
        api = twitter.API(
            consumer_key = settings.TWITTER_CONSUMER_KEY,
            consumer_secret = settings.TWITTER_CONSUMER_SECRET,
            access_token_key = settings.TWITTER_ACCESS_TOKEN,
            access_token_secret = settings.TWITTER_ACCESS_TOKEN_SECRET
        )
    return api

def getSocialDjangoAuth(username):
    "get Python-Twitter API object"
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return get_api()
    try:
        user_social_auth = UserSocialAuth.objects.get(user=user)
    except UserSocialAuth.DoesNotExist:
        return get_api()
    if (user_social_auth.provider != "twitter"):
        return get_api() 
        api = twitter.API(
        consumer_key = settings.SOCIAL_AUTH_TWITTER_KEY,
        consumer_secre = settings.SOCIAL_AUTH_TWITTER_SECRET,
        access_token_key = user_social_auth.extra_data["access_token"]["oauth_token"],
        access_token_secret = user_social_auth.extra_data["access_token"]["oauth_token_secret"],
    )
    return api