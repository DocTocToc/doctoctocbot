from datetime import datetime

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from bot.models import Account
from dm.models import DirectMessage


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
        #"kwargs"]["message_create"]["message_data"]
        if value == 'yes':
            return queryset.filter(
                Q(jsn__kwargs__message_create__message_data__has_key='quick_reply_response') |
                Q(jsn__has_key='quick_reply_response')
            )
        elif value == 'no':
            return queryset.exclude(
                Q(jsn__kwargs__message_create__message_data__has_key='quick_reply_response') |
                Q(jsn__has_key='quick_reply_response')
            )
        return queryset


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
        if value == 'yes':
            return queryset.filter(
                Q(jsn__has_key='quick_reply') |
                Q(jsn__kwargs__message_create__message_data__has_key='quick_reply')
            )
        elif value == 'no':
            return queryset.exclude(
                Q(jsn__has_key='quick_reply') |
                Q(jsn__kwargs__message_create__message_data__has_key='quick_reply')
            )
        return queryset


class DirectMessageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created_timestamp',
        'datetime_str',
        'sender_id',
        'recipient_id',
        'text',
        'is_quick_reply_response',
    )
    fields = (
        'id',
        'created_timestamp',
        'datetime_str',
        'sender_id',
        'recipient_id',
        'text',
        'is_quick_reply_response',
        'is_quick_reply_question',
        'jsn',
    )
    readonly_fields = (
        'id',
        'sender_id',
        'created_timestamp',
        'recipient_id',
        'text',
        'is_quick_reply_response',
        'is_quick_reply_question',
        'datetime_str'
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

    def datetime_str(self, obj):
        dt = datetime.fromtimestamp(obj.created_timestamp/1000)
        return f"{dt:%Y-%m-%d %H:%M:%S%z}"

    datetime_str.short_description = "Date & Time"
    
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

admin.site.register(DirectMessage, DirectMessageAdmin)