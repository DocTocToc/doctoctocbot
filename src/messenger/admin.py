from django.contrib import admin
from django.utils.translation import gettext as _
from messenger.models import (
    Message,
    Campaign,
    Receipt,
    CampaignMessage,
    MessengerCrowdfunding,
    Status,
    StatusLog,
)
from bot.models import Account
from moderation.models import SocialUser
from constance import config
from django.db.models import Count, DurationField
from textareacounter.admin import TextAreaCounterAdminMixin
from durationwidget.widgets import TimeDurationWidget
from django.utils.safestring import mark_safe


class AccountListFilter(admin.SimpleListFilter):
    title = _('account')
    parameter_name = 'account'

    def lookups(self, request, model_admin):
        account_id: List[int] = list(
            Account.objects.values_list('userid', flat=True)
        )
        return (
            [(str(su.user_id), su.screen_name_tag(),)
            for su in SocialUser.objects.filter(user_id__in=account_id)]
        )
    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(
            account=SocialUser.objects.get(
                user_id=int(self.value())
            )
        )


class CampaignMessageInline(admin.TabularInline):
    model = CampaignMessage
    extra = 1


class MessengerCrowdfundingInline(admin.TabularInline):
    model = MessengerCrowdfunding
    extra = 1


class CampaignAdmin(admin.ModelAdmin):
    formfield_overrides = {
        DurationField: {'widget': TimeDurationWidget},
    }
    inlines = (
        CampaignMessageInline,
        MessengerCrowdfundingInline,
    )
    raw_id_fields = ('account', 'recipients')
    list_display  = (
        'name',
        'account',
        'restrict_by_category',
        'restrict_by_crowdfunding',
        'restrict_by_last_investment',
        'retweet_range',
        'recipients_count_tag',
        'created',
        'updated',
        'backoff',
        'active',
        'start',
        'end',
        'send_status',
        'status_delay',
        'status',
    )
    fields = (
        'name',
        'account',
        'restrict_by_category',
        'categories',
        'restrict_by_crowdfunding',
        'crowdfunding_campaign',
        'retweet_range',
        'recipients',
        'recipients_socialuser_tag',
        'recipients_count_tag',
        'created',
        'updated',
        'backoff',
        'active',
        'start',
        'end',
        'send_status',
        'status_delay',
        'status',
    )
    readonly_fields = (
        'recipients_socialuser_tag',
        'recipients_count_tag',
        'created',
        'updated',
    )
    list_filter = [
        AccountListFilter,
        'active',
    ]

    def get_queryset(self, request):
        qs = super(CampaignAdmin, self).get_queryset(request)
        return qs.annotate(recipients_count=Count('recipients'))

    def recipients_count_tag(self, obj):
        return obj.recipients_count

    recipients_count_tag.admin_order_field = ('-recipients_count')
    recipients_count_tag.description_field = ('recipients count')

    def recipients_socialuser_tag(self, obj):
        return mark_safe(
            " ".join(
                [f'@{obj.screen_name_tag()}' for obj in obj.recipients.all()]
            )
        )

    recipients_socialuser_tag.short_description = 'Recipients'


class EventIdListFilter(admin.SimpleListFilter):

    title = _('Has event Id')

    parameter_name = 'has_event_id'

    def lookups(self, request, model_admin):

        return (
            ('yes', _('Yes')),
            ('no',  _('No')),
        )

    def queryset(self, request, queryset):

        if self.value() == 'yes':
            return queryset.filter(event_id__isnull=False)

        if self.value() == 'no':
            return queryset.filter(event_id__isnull=True)

class ReceiptAdmin(admin.ModelAdmin):
    list_per_page = config.messenger__admin__receipt_list_per_page
    list_display = (
        'campaign',
        'message',
        'user',
        'event_id',
        'error',
        'created',
    )
    search_fields = (
        'user',
        'event_id',
    )
    list_filter = [
        'campaign',
        'message',
        EventIdListFilter,
        'created',
    ]
    fields = (
        'campaign',
        'message',
        'user',
        'event_id',
        'error',
        'created',
        'updated',
    )
    readonly_fields = (
        'campaign',
        'message',
        'user',
        'event_id',
        'error',
        'created',
        'updated',
    )

class StatusAdmin(TextAreaCounterAdminMixin, admin.ModelAdmin):
    list_display = (
        'name',
        'content',
        'created', 
    )


class StatusLogAdmin(admin.ModelAdmin):
    list_display = (
        'campaign',
        'status',
        'user',
        'statusid',
        'error',
        'created',
    )
    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(StatusLog, StatusLogAdmin)
admin.site.register(Message)
admin.site.register(Status, StatusAdmin)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(Receipt, ReceiptAdmin)