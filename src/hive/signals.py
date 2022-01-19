import logging
import sys
from django.utils import timezone
from django.db.models.signals import m2m_changed
from conversation.models import Tweetdj, TwitterLanguageIdentifier
from hive.models import TweetSubscription, NotificationLog
from hive.notification import notify 
from django.dispatch import receiver
from bot.lib.status import api_switch_get_status
from bot.lib.statusdb import Addstatus
from hive.utils import (
    is_retweeted_by_categories,
    is_retweeted_by_categories_count
)

logger = logging.getLogger(__name__)

@receiver(m2m_changed, sender=Tweetdj.retweeted_by.through)
def retweeted_by_changed(sender, instance, action, **kwargs):
    if action == "post_add":
        if TweetSubscription.objects.filter(
            retweet_count__lte=instance.retweeted_by.all().count(),
            active=True
        ).exists():
            if not instance.json:
                status = api_switch_get_status(instance.statusid)
                if status:
                    add_status = Addstatus(status._json)
                    add_status.addtweetdj(update=True)
                else:
                    return
            instance.refresh_from_db()
            try:
                lang_tag = instance.json["lang"]
            except:
                e = sys.exc_info()[0]
                logger.debug(e)
                lang_tag = None
            try:
                lang_id = TwitterLanguageIdentifier.objects.get(tag=lang_tag)
            except TwitterLanguageIdentifier.DoesNotExist:
                lang_id = None
            age =  timezone.now() - instance.created_at
            for ts in TweetSubscription.objects.filter(
                retweet_count__lte=instance.retweeted_by.all().count(),
                active=True,
                language__in=[lang_id],
                age__gte=age,
            ):
                if not NotificationLog.objects.filter(
                    statusid=instance.statusid,
                    socialuser=ts.socialuser,
                    success=True,
                    ).exists() \
                    and is_retweeted_by_categories(
                        tweetdj=instance,
                        rt_target=ts.retweet_count,
                        category=ts.category.all()
                    ):
                    # archive image of notified status
                    add_status = Addstatus(instance.json)
                    add_status.add_image()
                    notify(
                        statusid=instance.statusid,
                        json=instance.json,
                        socialuser=ts.socialuser,
                        tweetsubscription=ts,
                        dct=is_retweeted_by_categories_count(
                            tweetdj=instance,
                            category=ts.category.all()
                        )
                    )

@receiver(m2m_changed, sender=Tweetdj.retweeted_by.through)
def quoted_by_changed(sender, instance, *args, **kwargs):
    pass