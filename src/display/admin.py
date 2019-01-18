from django.contrib import admin

from .models import WebTweet


class WebTweetAdmin(admin.ModelAdmin):
    list_display = ('statusid', 'conversationid', 'username', 'text',
                    'reply', 'answer', 'like', 'retweet', 'parentid')
    search_fields = ['statusid', 'username', 'text', 'conversationid', 'parentid']
    fields = ('statusid',
                        'conversationid',
                        'userid',
                        'username',
                        'name',
                        'time',
                        'html',
                        'text',
                        'reply',
                        'answer',
                        'like',
                        'retweet',
                        'parentid',
                        'rtl',
                        'image0',
                        'image1',
                        'image2',
                        'image3',
                        'avatar_mini',
                        'avatar_normal',
                        'avatar_bigger',)

    readonly_fields = ('statusid',
                        'conversationid',
                        'userid',
                        'username',
                        'name',
                        'time',
                        'html',
                        'text',
                        'reply',
                        'answer',
                        'like',
                        'retweet',
                        'parentid',
                        'rtl',
                        'image0',
                        'image1',
                        'image2',
                        'image3',
                        'avatar_mini',
                        'avatar_normal',
                        'avatar_bigger',)

admin.site.register(WebTweet, WebTweetAdmin)