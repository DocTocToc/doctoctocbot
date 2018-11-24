from django.contrib import admin

from .models import Treedj, Tweetdj


class TweetdjAdmin(admin.ModelAdmin):
    list_display = ('statusid', 'userid', 'screen_name_tag', 'status_text_tag', 'status_url_tag', 'hashtag0', 'hashtag1', 'created_at', 'quotedstatus', 'retweetedstatus',)
    search_fields = ['statusid', 'userid']
    fields = ('statusid', 'userid', 'screen_name_tag', 'status_text_tag', 'status_url_tag', 'json', 'hashtag0', 'hashtag1', 'created_at', 'quotedstatus', 'retweetedstatus',)
    readonly_fields = ('statusid', 'userid', 'screen_name_tag', 'status_text_tag', 'status_url_tag', 'json', 'created_at', 'quotedstatus', 'retweetedstatus',)

admin.site.register(Treedj)
admin.site.register(Tweetdj, TweetdjAdmin)