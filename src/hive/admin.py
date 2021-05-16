from django.contrib import admin
from django.db import models

from hive.models import (
    TweetSubscription,
    NotificationService,
    NotificationLog,
)

from modeltranslation.admin import TranslationAdmin
from durationwidget.widgets import TimeDurationWidget


class TweetSubscriptionAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.DurationField: {'widget': TimeDurationWidget},
    }
    list_display = (
        'id',
        'socialuser',
#        'language',
        'quote_count',
        'retweet_count',
        'broadcast_count',
#        'category',
        'age',
        'active',
    )
    autocomplete_fields = [
        'socialuser',
        'language',
        'category',
    ]


class NotificationServiceAdmin(TranslationAdmin):
    list_display = (
       'name',
       'label_en',
       'label_fr',
       'description_en',
       'description_fr',
    )


class NotificationLogAdmin(admin.ModelAdmin):
    list_display = (
        'statusid',
        'tweetsubscription',
        'socialuser',
        'service',
        'success',
        'success_log',
        'error_log',
        'created',
        'updated',
    )

admin.site.register(TweetSubscription, TweetSubscriptionAdmin)
admin.site.register(NotificationService, NotificationServiceAdmin)
admin.site.register(NotificationLog, NotificationLogAdmin)