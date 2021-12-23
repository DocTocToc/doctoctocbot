from datetime import datetime

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from bot.models import Account
from dm.models import DirectMessage

from moderation.admin_tags import (
    admin_tag_social_user_img,
    admin_tag_screen_name_link
)
from django.utils.safestring import mark_safe
from constance import config

class ToAccount(admin.SimpleListFilter):
    title = 'To Account'
    parameter_name = 'to_account'
    
    def lookups(self, request, model_admin):
        return list(Account.objects.values_list('userid', 'username'))

    def queryset(self, request, queryset):
        for userid in list(Account.objects.values_list('userid', flat=True)):
            if self.value() == str(userid):
                return queryset.filter(recipient_id=userid)

            
class FromAccount(admin.SimpleListFilter):
    title = 'From Account'
    parameter_name = 'from_account'
    
    def lookups(self, request, model_admin):
        return list(Account.objects.values_list('userid', 'username'))

    def queryset(self, request, queryset):
        for userid in list(Account.objects.values_list('userid', flat=True)):
            if self.value() == str(userid):
                return queryset.filter(sender_id=userid)


class IsQuickReplyResponse(admin.SimpleListFilter):
    title = 'Quick Reply Response'
    parameter_name = 'is_quick_reply_response'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        value = self.value()
        q2= (
            Q(jsn__has_key='kwargs') &
            Q(jsn__kwargs__message_create__message_data__has_key='quick_reply_response')
        )
        q1=Q(jsn__has_key='quick_reply_response')
        if value == 'yes':
            return queryset.filter(q1 | q2).order_by("-created_timestamp")
        elif value == 'no':
            return queryset.exclude(q1 | q2).order_by("-created_timestamp")
        return queryset.order_by("-created_timestamp")


class IsQuickReplyQuestion(admin.SimpleListFilter):
    title = 'Quick Reply Question'
    parameter_name = 'is_quick_reply_question'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        value = self.value()
        q1 = Q(jsn__has_key='quick_reply')
        q2= (
            Q(jsn__has_key='kwargs') &
            Q(jsn__kwargs__message_create__message_data__has_key='quick_reply')
        )
        if value == 'yes':
            return queryset.filter(q1 | q2).order_by("-created_timestamp")
        elif value == 'no':
            return queryset.exclude(q1 | q2).order_by("-created_timestamp")
        return queryset


class DirectMessageAdmin(admin.ModelAdmin):
    list_per_page = config.dm__admin__direct_message_list_per_page
    list_display = (
        'id_tag',
        'dm_link_tag',
        'from_img_tag',
        'from_screen_name_tag',
        'to_img_tag',
        'to_screen_name_tag',
        'datetime_str_tag',
        'text_tag',
        'is_quick_reply_response',
        'is_quick_reply_question',
    )
    fields = (
        'id',
        'dm_link_tag',
        'created_timestamp',
        'datetime_str',
        'from_img_tag',
        'from_screen_name_tag',
        'sender_id',
        'to_img_tag',
        'to_screen_name_tag',
        'recipient_id',
        'text',
        'is_quick_reply_response',
        'is_quick_reply_question',
        'jsn',
    )
    readonly_fields = (
        'id',
        'dm_link_tag',
        'from_img_tag',
        'from_screen_name_tag',
        'sender_id',
        'created_timestamp',
        'datetime_str',
        'to_img_tag',
        'to_screen_name_tag',
        'recipient_id',
        'text',
        'is_quick_reply_response',
        'is_quick_reply_question',
        'jsn',
    )
    search_fields = (
        'jsn__kwargs__message_create__message_data__text',
        'jsn__text',
    )
    list_filter = (
        IsQuickReplyResponse,
        IsQuickReplyQuestion,
        FromAccount,
        ToAccount, 
    )

    def text_tag(self, obj):
        return obj.text[0:140]

    text_tag.short_description = "Text"

    def datetime_str_tag(self, obj):
        dt = datetime.fromtimestamp(obj.created_timestamp/1000)
        return dt.strftime("%Y-%m-%d %H:%M:%S%z")

    datetime_str_tag.short_description = "Date & Time"
    
    def is_quick_reply_response(self, obj):
        try:
            obj.jsn["kwargs"]["message_create"]["message_data"]["quick_reply_response"]
            return True
        except KeyError:
            try:
                obj.jsn["quick_reply_response"]
                return True
            except KeyError:
                return False

    is_quick_reply_response.boolean = True
    is_quick_reply_response.short_description = 'QR Response'
    
    def is_quick_reply_question(self, obj):
        try:
            obj.jsn["kwargs"]["message_create"]["message_data"]["quick_reply"]
            return True
        except KeyError:
            try:
                obj.jsn["quick_reply"]
                return True
            except KeyError:
                return False

    is_quick_reply_question.boolean = True
    is_quick_reply_question.short_description = 'QR Question'
    
    def from_img_tag(self, obj):
        return admin_tag_social_user_img(obj.sender_id)

    from_img_tag.short_description = "From"
    
    def to_img_tag(self, obj):
        return admin_tag_social_user_img(obj.recipient_id)

    to_img_tag.short_description = "To"
    
    def from_screen_name_tag(self, obj):
        return admin_tag_screen_name_link(obj.sender_id)

    from_screen_name_tag.short_description = "From"
    
    def to_screen_name_tag(self, obj):
        return admin_tag_screen_name_link(obj.recipient_id)

    to_screen_name_tag.short_description = "To"
    
    def id_tag(self, obj):
        return '\N{ENVELOPE}'
        
    id_tag.short_description = "ID"

    def dm_link_tag(self, obj):
        text = '\N{BIRD}'
        href = (
            f"https://twitter.com/messages/{obj.recipient_id}-{obj.sender_id}"
        )
        return mark_safe(
            f'<a href="{href}">{text}</a>'
        )
    dm_link_tag.short_description = "DM"

admin.site.register(DirectMessage, DirectMessageAdmin)