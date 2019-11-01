import logging 
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.contrib.staticfiles.templatetags.staticfiles import static

from versions.admin import VersionedAdmin

from tagging.models import Queue, Process, Category
from community.models import Community
from conversation.models import Tweetdj

from moderation.models import (
    SocialUser,
    SocialMedia,
)

logger = logging.getLogger(__name__)

def status_tag(obj):
    tweetdj = get_tweetdj(obj)
    if tweetdj:
        return tweetdj.getstatustext(tweetdj.statusid)[:140]


def socialuser_link(obj):
    if obj.socialmedia == twitter_socialmedia():
        su = get_socialuser(obj)
        if su:
            return mark_safe(
                '<a href="{link}">{tag}</a>'.format(
                    link = reverse("admin:moderation_socialuser_change", args=(su.pk,)),
                    tag = su.screen_name_tag()
                )
            )

def mini_image_tag(obj):
    su = get_socialuser(obj)
    if su:
        if profile(obj) is not None:
            p = profile(obj)
            url = p.miniavatar.url
        else:
            url = static("moderation/twitter_unknown_images/egg24x24.png")
    
    return mark_safe('<img src="%s"/>' % url)

def profile(obj):
    su = get_socialuser(obj)
    if not su:
        return None
    if hasattr(su, 'profile'):
        return su.profile
    else:
        return None

def twitter_socialmedia():
    try:
        return SocialMedia.objects.get(name="twitter")
    except SocialMedia.DoesNotExist:
        return

def get_tweetdj(obj):
    if type(obj) is Queue:
        try:
            return Tweetdj.objects.get(statusid=obj.uid)
        except Tweetdj.DoesNotExist:
            return
    elif type(obj) is Process:
        try:
            return Tweetdj.objects.get(statusid=obj.queue.uid)
        except Tweetdj.DoesNotExist:
            return

def get_socialuser(obj):
    tweetdj = get_tweetdj(obj)
    if not tweetdj:
        return
    return tweetdj.socialuser

def tweet_link(obj):
    if type(obj) is Queue:
        _statusid = obj.uid
    elif type(obj) is Process:
        _statusid = obj.queue.uid
    try:
        screen_name = get_socialuser(obj).screen_name_tag()
    except TypeError:
        pass
    except AttributeError:
        screen_name = "_"
    return mark_safe(
        '<a href="https://twitter.com/{screen_name}/status/{status_id}" target="_blank"alt="{status_id}">🐦</a>'.format(
            screen_name = screen_name,
            status_id = _statusid
        )
    )

def tweetdj_link(self, obj):
    """
    Return a link to the corresponding Tweetdj object admin page
    """
    if type(obj) is Queue:
        _statusid = obj.uid
    elif type(obj) is Process:
        _statusid = obj.queue.uid

    if Tweetdj.objects.filter(statusid=_statusid).exists():
        return mark_safe(
            '<a href="{}">🗃️</a>'
            .format(
                reverse("admin:conversation_tweetdj_change", args=(_statusid,))
            )
        )
    else:
        return "❌"


class QueueAdmin(VersionedAdmin):
    list_display = (
        'mini_image_tag',
        'socialuser_link',
        'name_tag',
        'uid',
        'status_tag',
        'tweet_link',
        'status_object',
        'socialmedia',
        'community',
    )
    readonly_fields = (
        'uid',
        'mini_image_tag',
        'socialuser_link',
        'name_tag',
        'status_tag',
        'tweet_link',
        'status_object',
        'community',
        'socialmedia',
    )
    list_display_show_identity = False
    list_display_show_end_date = False
    list_display_show_start_date = True


    
    def profile(self, obj):
        return profile(obj)
    
    def socialuser_link(self, obj):
        return socialuser_link(obj)

    socialuser_link.short_description = 'SocialUser'
    

    def tweet_link(self, obj):
        return tweet_link(obj)
    
    tweet_link.short_description = "Tweet"

    def status_object(self, obj):
        return tweetdj_link(self, obj)
    
    status_object.short_description = "Status"

    def mini_image_tag(self, obj):
        return mini_image_tag(obj)
    
    mini_image_tag.short_description = 'Image'

    def name_tag(self, obj):
        p = self.profile(obj)
        if p:
            return p.json.get("name", None)
        else:
            return None
    
    name_tag.short_description = 'Name'

    def status_tag(self, obj):
        return status_tag(obj)

    status_tag.short_description = 'Text'


class ProcessAdmin(VersionedAdmin):
    list_display = (
        'queue_link',
        'processor_mini_image_tag',
        'processor_socialuser_link',
        'processed_mini_image_tag',
        'processed_socialuser_link',
        'status_tag',
        'tweet_link',
        'status_object',
    )
    fields = (
        'queue_link',
        'processor_mini_image_tag',
        'processor_socialuser_link',
        'processed_mini_image_tag',
        'processed_socialuser_link',
        'status_tag',
        'tweet_link',
        'status_object',
        'id',
        'identity',
    )
    readonly_fields = (
        'queue_link',
        'processor_mini_image_tag',
        'processor_socialuser_link',
        'processed_mini_image_tag',
        'processed_socialuser_link',
        'status_tag',
        'tweet_link',
        'status_object',    
    )
    list_display_show_identity = True
    list_display_show_end_date = True
    list_display_show_start_date = True

    def profile(self, obj):
        return profile(obj)

    def queue_link(self, obj):
        try:
            q = Queue.objects.get(id=obj.queue.id)
            return mark_safe(
                '<a href="{link}">Q</a>'.format(
                    link = reverse("admin:tagging_queue_change", args=(q.id,))
                )
            )
        except Queue.DoesNotExist as e:
            logger.error("Queue does not exist.", e)
            return "🚫"
    
    queue_link.short_description = 'Queue'

    def processed_mini_image_tag(self, obj):
        return mini_image_tag(obj)

    processed_mini_image_tag.short_description = 'Processed'
    
    def processor_mini_image_tag(self, obj):
        if hasattr(obj.processor, 'profile'):
            url = obj.processor.profile.miniavatar.url
        else:
            url = static("moderation/twitter_unknown_images/egg24x24.png")
        return mark_safe('<img src="%s"/>' % url)

    processor_mini_image_tag.short_description = 'Processor'
    
    def processor_socialuser_link(self, obj):
        return mark_safe(
            '<a href="{link}">{tag}</a>'.format(
                link = reverse("admin:moderation_socialuser_change", args=(obj.processor.pk,)),
                tag = obj.processor.screen_name_tag()
            )
        )

    processor_socialuser_link.short_description = 'Processor'

    def processed_socialuser_link(self, obj):
        return socialuser_link(obj.queue)

    processed_socialuser_link.short_description = 'Processed'

    def status_tag(self, obj):
        return status_tag(obj)

    status_tag.short_description = 'Text'
    
    def tweet_link(self, obj):
        return tweet_link(obj)
    
    tweet_link.short_description = "Tweet"

    def status_object(self, obj):
        return tweetdj_link(self, obj)
    
    status_object.short_description = "Status"


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'tag',
        'hashtag',
        'summary',
        'description',
        'order',   
    )

admin.site.register(Queue, QueueAdmin)
admin.site.register(Process, ProcessAdmin)
admin.site.register(Category, CategoryAdmin)