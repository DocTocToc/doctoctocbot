import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from request.models import Queue
from dm.api import senddm
from django.utils.translation import gettext as _
from moderation.models import Category
from django.template import Template, Context
from community.helpers import site_url
from django.urls import reverse
from bot.tweepy_api import get_api
from community.helpers import activate_language

logger = logging.getLogger(__name__) 

@receiver(post_save, sender=Queue)
def dm_admin(sender, instance, created, **kwargs):
    if (
        created
        and (instance.state == Queue.PENDING)
        and (instance.id == instance.identity)
    ):
        try:
            screen_name = instance.socialuser.screen_name_tag()
        except:
            screen_name = None
        activate_language(instance.community)
        community_name = instance.community.name
        if screen_name:
            text = _("Please handle @{screen_name} follow request for {community_name} community.").format(
                screen_name=screen_name,
                community_name=community_name
            )
        else:
            text = _("You have a new follow request.")
        
        try:
            dev_cat = Category.objects.get(name='dev')
            logger.debug(dev_cat)
        except Category.DoesNotExist:
            return
        try:
            screen_name = instance.community.account.username
        except:
            return
        for dev in dev_cat.socialuser_set.all(): 
            dm = senddm(
                text=text,
                user_id=dev.user_id,
                screen_name=screen_name
            )
            logger.debug(dm)
    
@receiver(post_save, sender=Queue)
def message_requestor(sender, instance, created, **kwargs):
    if (
        created
        and (instance.state == Queue.PENDING)
        and (instance.id == instance.identity)
    ):
        try:
            community = instance.community
        except:
            return
        try:
            helper_username = community.helper.username
        except:
            return
        if not helper_username:
            return
        try:
            requestor_screen_name = instance.socialuser.screen_name_tag()
        except:
            return
        if not requestor_screen_name:
            return
        try:
            bot_username = community.account.username
        except:
            return
        
        helper_message = get_helper_message(
            community=community,
            requestor_screen_name=requestor_screen_name,
            bot_username=bot_username,            
        )
        api = get_api(username=helper_username, backend=True)
        api.update_status(helper_message)


def get_helper_message(community, requestor_screen_name, bot_username):
    db_message = community.helper_message
    if not db_message:
        return
    url = f"{site_url(community)}{reverse('moderation:self')}"
    context = {
        'requestor': requestor_screen_name,
        'bot': bot_username,
        'url': url,
    }
    db_template = Template(db_message)
    return db_template.render(Context(context))
                