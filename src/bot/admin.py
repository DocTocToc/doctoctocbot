from django.contrib import admin

from bot.models import Account, Greet

class AccountAdmin(admin.ModelAdmin):
    fields = (
        'userid',
        'username',
        'password',
        'email',
        'phone',
        'twitter_consumer_key',
        'twitter_consumer_secret',
        'twitter_access_token',
        'twitter_access_token_secret',
        'active',
        'hashtag',
        'launch',
        'backend_twitter_consumer_key',
        'backend_twitter_consumer_secret',
        'backend_twitter_access_token',
        'backend_twitter_access_token_secret',
        'protected',
    )
    readonly_fields = (
        'userid',
        'username',
    )


admin.site.register(Account, AccountAdmin)
admin.site.register(Greet)
