from django.contrib import admin
from bot.models import Account, Greet

class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'userid',
        'username',
        'socialuser',
        'password_hidden',
        'email',
        'phone',
        'cookies_tag',
        'twitter_consumer_key',
        'twitter_consumer_secret',
        'twitter_access_token',
        'twitter_access_token_secret',
        'active',
        'launch',
        'backend_twitter_consumer_key',
        'backend_twitter_consumer_secret',
        'backend_twitter_access_token',
        'backend_twitter_access_token_secret',
        'protected',
)
    fields = (
        'userid',
        'username',
        'socialuser',
        'password',
        'email',
        'phone',
        'cookies_tag',
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


admin.site.register(Account, AccountAdmin)
admin.site.register(Greet)
