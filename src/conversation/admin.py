from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from django.urls import reverse
from django.utils.safestring import mark_safe    

from .models import Treedj, Tweetdj


class TweetdjAdmin(admin.ModelAdmin):
    list_display = ('statusid', 'userid', 'screen_name_tag', 'status_text_tag', 'status_url_tag', 'hashtag0', 'hashtag1', 'created_at', 'quotedstatus', 'retweetedstatus',)
    search_fields = ['statusid', 'userid']
    fields = ('statusid', 'userid', 'screen_name_tag', 'status_text_tag', 'status_url_tag', 'json', 'hashtag0', 'hashtag1', 'created_at', 'quotedstatus', 'retweetedstatus',)
    readonly_fields = ('statusid', 'userid', 'screen_name_tag', 'status_text_tag', 'status_url_tag', 'json', 'created_at', 'quotedstatus', 'retweetedstatus',)

admin.site.register(Tweetdj, TweetdjAdmin)


class TreedjAdmin(MPTTModelAdmin):
    list_display = ('statusid', 'parent', 'status_text_tag', 'tweetdj_link', 'status_url_tag',)
    search_fields = ['statusid', 'parent__statusid']
    fields = ('statusid', 'parent', 'status_text_tag', 'tweetdj_link', 'status_url_tag',)
    readonly_fields = ('statusid', 'parent', 'status_text_tag', 'tweetdj_link', 'status_url_tag',)

    def tweetdj_link(self, obj):
        if Tweetdj.objects.filter(statusid=obj.statusid).exists():
            return mark_safe(
                '<a href="{}">🐦</a>'
                .format(
                    reverse("admin:conversation_tweetdj_change", args=(obj.statusid,))
                )
            )
    
    tweetdj_link.short_description = 'tweet'

admin.site.register(Treedj, TreedjAdmin)
