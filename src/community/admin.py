from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from reversion.admin import VersionAdmin

from community.models import (
    Community,
    Retweet,
    Trust,
    Cooperation,
    CommunityCategoryRelationship,
    TextDescription,
    Text,
)


class TrustInline(admin.TabularInline):
    model = Trust
    extra = 5
    fk_name = 'from_community'


class CooperationInline(admin.TabularInline):
    model = Cooperation
    extra = 5
    fk_name = 'from_community'
    
class CategoryInline(admin.TabularInline):
    model = CommunityCategoryRelationship
    extra = 5
    fk_name = 'community'


class CommunityAdmin(admin.ModelAdmin):
    inlines = [
        TrustInline,
        CooperationInline,
        CategoryInline,
    ]
    list_display = (
        'name',
        'active',
        'account',
        'helper',
        'created',
        'site',
        'allow_unknown',
        'language',
        'pending_moderation_period',
        'viral_moderation',
    )
    fields = (
        'name',
        'active',
        'account',
        'helper',
        'helper_message',
        'hashtag',
        'membership',
        'follower',
        'created',
        'site',
        'crowdfunding',
        'allow_unknown',
        'language',
        'pending_moderation_period',
        'viral_moderation',
        'viral_moderation_category',
        'viral_moderation_message',
        'follow_request_backoff',
        'request_queue_backoff',
        'follower_common_account',
    )
    readonly_fields = (
        'created',
    )
    

class RetweetAdmin(admin.ModelAdmin):
    list_display = (
        'community',
        'hashtag',
        'category',
        'retweet',  
    )


class TextDescriptionAdmin(TranslationAdmin):
    pass


@admin.register(Text)
class TextAdmin(VersionAdmin):

    pass


admin.site.register(Community, CommunityAdmin)
admin.site.register(Retweet, RetweetAdmin)
admin.site.register(TextDescription, TextDescriptionAdmin)
