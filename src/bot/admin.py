from django.contrib import admin
from bot.models import (
    Account,
    Greet,
    TwitterApp,
    TwitterScopes,
    TwitterAPI,
    AccessToken,
)

class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'userid',
        'username',
        'socialuser',
        'app',
        'password_hidden',
        'email',
        'phone',
        'cookies_tag',
        'active',
        'launch',
        'twitter_consumer_key',
        'twitter_consumer_secret',
        'twitter_access_token',
        'twitter_access_token_secret',
        'protected',
)
    fields = (
        'userid',
        'username',
        'socialuser',
        'app',
        'password',
        'email',
        'phone',
        'cookies_tag',
        'active',
        'hashtag',
        'launch',
        'twitter_consumer_key',
        'twitter_consumer_secret',
        'twitter_access_token',
        'twitter_access_token_secret',
        'protected',
    )
    readonly_fields = (
        'userid',
        'username',
        'cookies_tag',
        'password_hidden',
    )
    autocomplete_fields = ["socialuser"]
    
    def cookies_tag(self, obj):
        if obj.cookies:
            return "🗎"
        else:
            return "🗋"
        
    def password_hidden(self, obj):
        if obj.password:
            return "🗎"
        else:
            return "🗋"


@admin.register(TwitterApp)
class TwitterAppAdmin(admin.ModelAdmin):
    list_display = (
        'app_id',
        'name',
        'description',
        'api',
    )


@admin.register(TwitterScopes)
class TwitterScopesAdmin(admin.ModelAdmin):
    list_display = (
        'scope',    
    )


@admin.register(TwitterAPI)
class TwitterAPIAdmin(admin.ModelAdmin):
        list_display = (
        'name',    
    )


@admin.register(AccessToken)
class AccessTokenAdmin(admin.ModelAdmin):
        list_display = (
        'oauth',
        'account',
        'app',
        'created',
        'updated',
    )

admin.site.register(Account, AccountAdmin)
admin.site.register(Greet)