from django.contrib import admin
from django.utils.translation import gettext as _
from messenger.models import (
    Message,
    Campaign,
    Receipt,
    CampaignMessage,
    MessengerCrowdfunding,
)
from constance import config
from django.db.models import Count


class CampaignMessageInline(admin.TabularInline):
    model = CampaignMessage
    extra = 1


class MessengerCrowdfundingInline(admin.TabularInline):
    model = MessengerCrowdfunding
    extra = 1


class CampaignAdmin(admin.ModelAdmin):
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
        'retweet_range',
        'recipients_count_tag',
        'created',
        'updated',
        'backoff',
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
        'recipients_count_tag',
        'created',
        'updated',
        'backoff',
    )
    readonly_fields = (
        'recipients_count_tag',
        'created',
        'updated',
    )

    def get_queryset(self, request):
        qs = super(CampaignAdmin, self).get_queryset(request)
        return qs.annotate(recipients_count=Count('recipients'))

    def recipients_count_tag(self, obj):
        return obj.recipients_count

    recipients_count_tag.admin_order_field = ('-recipients_count')
    recipients_count_tag.description_field = ('recipients count')


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

admin.site.register(Message)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(Receipt, ReceiptAdmin)