from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse

from versions.admin import VersionedAdmin
from moderation.models import SocialUser
from request.models import Queue

class QueueAdmin(VersionedAdmin):
    list_display = (
        'mini_image_tag',
        'screen_name_link',
        'state_tag',
        'uid',
        'socialuser',
        'community',
        'socialmedia',
    )
    readonly_fields = (
        'mini_image_tag',
        'screen_name_link',
        'uid',
        'socialuser',
        'community',
        'socialmedia',   
    )
    search_fields = (
        'socialuser__profile__json__screen_name',
    )
    list_display_show_identity = False
    list_display_show_end_date = False
    list_display_show_start_date = True

    def state_tag(self, obj):
        if obj.state == Queue.PENDING:
            return "pending⌛"
        else:
            return obj.state

    state_tag.short_description = 'STATE'
    
    def screen_name_link(self, obj):
        try:
            su = SocialUser.objects.get(user_id=obj.uid)
            return mark_safe(
                '<a href="{link}">{tag}</a>'.format(
                    link = reverse("admin:moderation_socialuser_change", args=(su.pk,)),
                    tag = obj.socialuser.screen_name_tag()
                )
            )
        except SocialUser.DoesNotExist:
            return obj.socialuser.screen_name_tag()
    
    screen_name_link.short_description = 'Screen name'
    
    def mini_image_tag(self, obj):
        from django.contrib.staticfiles.templatetags.staticfiles import static
        p = obj.socialuser.profile
        if p:
            url = p.miniavatar.url
        else:
            url = static("moderation/twitter_unknown_images/egg24x24.png")
        
        return mark_safe('<img src="%s"/>' % url)
    
    mini_image_tag.short_description = 'Image'

admin.site.register(Queue, QueueAdmin)