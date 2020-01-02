from celery import shared_task
from community.models import Community
from request.twitter_request import get_incoming_friendship
from request.models import Queue
from moderation.models import addsocialuser_from_userid, SocialMedia
from moderation.tasks import handle_create_update_profile


@shared_task
def handle_incoming_friendship():
    for community in Community.objects.all():
        for uid in get_incoming_friendship(community):
            try:
                queue = Queue.objects.current.get(
                    uid=uid,
                    community=community
                )
            except Queue.DoesNotExist:
                try:
                    queue = Queue.objects.get(
                        uid=uid,
                        community=community
                    )
                    queue = queue.clone()
                    queue.state = Queue.PENDING
                    queue.save()
                except Queue.DoesNotExist:
                    try:
                        socialmedia = SocialMedia.objects.get(name='twitter')
                    except SocialMedia.DoesNotExist:
                        return
                    socialuser = addsocialuser_from_userid(uid)
                    if not socialuser:
                        return
                    handle_create_update_profile(uid)
                    queue = Queue.objects.create(
                        uid=uid,
                        socialmedia=socialmedia,
                        socialuser=socialuser,
                        community=community,
                        state=Queue.PENDING
                    )