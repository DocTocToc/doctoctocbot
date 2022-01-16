from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from reversion.admin import VersionAdmin
from durationwidget.widgets import TimeDurationWidget
from django.db import models

from community.models import (
    Community,
    Retweet,
    Trust,
    Cooperation,
    CommunityCategoryRelationship,
    TextDescription,
    Text,
    AccessLevel,
    ApiAccess,
    Blog,
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
        'pending_self_moderation_period',
        'moderator_moderation_period',
        'viral_moderation',
        'tree_search',
        'no_root_backoff',
        'tree_search_retry',
        'twitter_follow_member',
        'twitter_request_dm',
        'blog',
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
        'pending_self_moderation_period',
        'moderator_moderation_period',
        'viral_moderation',
        'viral_moderation_category',
        'viral_moderation_message',
        'tree_search',
        'no_root_backoff',
        'tree_search_retry',
        'follow_request_backoff',
        'request_queue_backoff',
        'follower_common_account',
        'twitter_follow_member',
        'twitter_request_dm',
        'twitter_request_dm_text',
        'twitter_self_moderation_dm',
        'blog',
        'members_friends_cache',
    )
    readonly_fields = (
        'created',
    )
    formfield_overrides = {
        models.DurationField: {'widget': TimeDurationWidget},
    }


class RetweetAdmin(admin.ModelAdmin):
    list_display = (
        'community',
        'hashtag',
        'category',
        'retweet',
        'favorite',  
    )
    list_filter = (
        'community',
        'hashtag',
        'category',
    )


class TextDescriptionAdmin(TranslationAdmin):
    pass


class TextCommunityInline(admin.TabularInline):
    model = Text.community.through


@admin.register(Text)
class TextAdmin(VersionAdmin):
    inlines = [
        TextCommunityInline,    
    ]
    fields = (
        'type',
        'content',
    )


class AccessLevelAdmin(TranslationAdmin):
    list_display = (
        'pk',
        'name',
    )
    ordering = ('pk',)
    
class ApiAccessAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'community',
        'level',
        'status_limit',
        'status_rate',
        'author_category',
        'author_specialty',
        'search_datetime',
        'search_category',
        'search_tag',
        'status_category',
        'status_tag',
        'status_protected',
        'status_media',
        'reply_count',
        'filter_author_self',
    )
    list_filter = (
    'community',
    'level',
    )
    ordering = ('community', 'level')


class BlogAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'link',
        'url',
    )


admin.site.register(Community, CommunityAdmin)
admin.site.register(Retweet, RetweetAdmin)
admin.site.register(TextDescription, TextDescriptionAdmin)
admin.site.register(AccessLevel, AccessLevelAdmin)
admin.site.register(ApiAccess, ApiAccessAdmin)
admin.site.register(Blog, BlogAdmin)
