import logging
from django.conf import settings
from moderation.tasks import handle_twitter_followers, handle_twitter_friends
from moderation.models import SocialMedia, SocialUser, Profile
from moderation.profile import avatar

logger = logging.getLogger('root')

def user(backend, user, response, *args, **kwargs):
    if backend.name == 'twitter':
        if user.socialuser is None:
            user.socialuser = kwargs['socialuser']
            user.save()

def socialuser(backend, user, response, *args, **kwargs):
    if backend.name == 'twitter':
        sm_mi, created1 = SocialMedia.objects.get_or_create(name=backend.name)
        tuid_int = kwargs['uid']
        su_mi, created2 = SocialUser.objects.get_or_create(user_id=tuid_int, social_media=sm_mi)

def profile(backend, user, response, *args, **kwargs):
    if backend.name == 'twitter':
        try:
            p = user.socialuser.profile
            p.json = response
            p.save()
        except Profile.DoesNotExist:
            p = Profile.objects.create(json=response, socialuser=user.socialuser) 
        avatar(p, response)

def network(backend, user, response, *args, **kwargs):
    if backend.name == 'twitter':
        screen_name = settings.SOCIAL_AUTH_TWITTER_SCREEN_NAME
        if not screen_name:
            return
        try:
            user_id = kwargs['uid']
        except:
            return
        handle_twitter_followers.apply_async(
            args=(
                user_id,
                screen_name,
            )
        )
        handle_twitter_friends.apply_async(
            args=(
                user_id,
                screen_name,
            )
        )