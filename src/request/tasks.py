from celery import shared_task
from community.models import Community
from request.twitter_request import get_incoming_friendship
from request.models import Queue
from moderation.models import addsocialuser_from_userid, SocialMedia
from moderation.tasks import handle_create_update_profile
from django.db.utils import DatabaseError
from moderation.profile import create_update_profile_twitter

@shared_task
def handle_incoming_friendship():
    for community in Community.objects.all():
        try:
            bot_screen_name = community.account.username
        except:
            bot_screen_name = None
        for uid in get_incoming_friendship(community):
            accept_pending_q_exists = Queue.objects.filter(
                uid=uid,
                community=community,
                state__in=[Queue.ACCEPT, Queue.PENDING],
            ).exists()
            if accept_pending_q_exists:
                continue

            decline_q_exists = Queue.objects.filter(
                uid=uid,
                community=community,
                state=Queue.DECLINE
            ).exists()
            if decline_q_exists:
                continue
            
            cancel_q_exists = Queue.objects.filter(
                uid=uid,
                community=community,
                state=Queue.CANCEL,
            ).exists()
            if cancel_q_exists:
                continue

            try:
                socialmedia = SocialMedia.objects.get(name='twitter')
            except SocialMedia.DoesNotExist:
                return
            socialuser = addsocialuser_from_userid(uid)
            if not socialuser:
                return
            try:
                create_update_profile_twitter(
                    socialuser,
                    bot_screen_name=bot_screen_name
                )
            except:
                continue
            try:
                Queue.objects.create(
                    uid=uid,
                    socialmedia=socialmedia,
                    socialuser=socialuser,
                    community=community,
                    state=Queue.PENDING
                )
            except DatabaseError:
                continue