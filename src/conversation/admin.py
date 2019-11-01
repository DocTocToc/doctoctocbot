from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from mptt.admin import MPTTModelAdmin
from django.urls import reverse
from django.utils.safestring import mark_safe
from rangefilter.filter import DateTimeRangeFilter
from moderation.models import Category, SocialUser
import logging
from multiprocessing import Pool
from common.utils import localized_tuple_list_sort
from moderation.models import SocialUser
from common.twitter import status_url_from_id

logger = logging.getLogger(__name__)

from .models import (
    Treedj,
    Tweetdj,
    Hashtag,
)


def screen_name_link(self, obj):
    if hasattr(obj, "json"):
        status = obj.json
        userid = obj.userid
    else:
        try:
            tweetdj = Tweetdj.objects.get(statusid=obj.statusid)
            status = tweetdj.json
            userid = tweetdj.userid
        except:
            return

    screen_name = ""
    if "user" in status:  
        if "screen_name" in status["user"]:
            screen_name = status["user"]["screen_name"]

    if screen_name:
        try:
            su = SocialUser.objects.get(user_id=userid)
            return mark_safe(
                '<a href="{link}">{name}</a>'
                .format(
                    link=reverse("admin:moderation_socialuser_change", args=(su.pk,)),
                    name=screen_name
                )
            )
        except:
            return screen_name


class CategoryListFilter(admin.SimpleListFilter):

    title = _('Category')

    parameter_name = 'category'

    def lookups(self, request, model_admin):
        lst = list(Category.objects.all().values_list('name', 'label'))
        if hasattr(settings, "SORTING_LOCALE"):
            pool = Pool()
            return pool.apply(localized_tuple_list_sort, [lst, 1, settings.SORTING_LOCALE])
        else:
            return localized_tuple_list_sort(lst, 1)

    def queryset(self, request, queryset):
        if self.value():
            userids = (
                SocialUser.objects.filter(
                    category=Category.objects.get(name=self.value())).
                values_list('user_id', flat=True)
            )
            return queryset.filter(userid__in=userids)
        else:
            return queryset


class TweetdjAdmin(admin.ModelAdmin):
    list_display = (
        'statusid',
        'userid',
        'socialuser',
        'screen_name',
        'status_text_tag',
        'status_link',
        'created_at',
        'quotedstatus',
        'retweetedstatus',
        'deleted',    
    )
    search_fields = ['statusid', 'userid', 'json',]
    fields = (
        'statusid',
        'userid',
        'socialuser',
        'screen_name',
        'status_text_tag',
        'status_url_tag',
        'json',
        'created_at',
        'quotedstatus',
        'retweetedstatus',
        'hashtag',
        'parentid',
        'tags',
    )
    readonly_fields = (
        'statusid',
        'userid',
        'socialuser',
        'screen_name',
        'status_text_tag',
        'status_url_tag',
        'json',
        'created_at',
        'quotedstatus',
        'retweetedstatus',
        'parentid',
    )
    list_filter = (
        ('created_at', DateTimeRangeFilter),
        'quotedstatus',
        'retweetedstatus',
        'deleted',
        CategoryListFilter,
        'hashtag',
    )
    
    def screen_name(self, obj):
        return screen_name_link(self,obj)

    screen_name.short_description = "Screen name"

    def status_link(self, obj):
        return mark_safe(f'<a href="{status_url_from_id(obj.statusid)}">🐦</a>')

    status_link.short_description = 'tweet'

admin.site.register(Tweetdj, TweetdjAdmin)


class TreedjAdmin(MPTTModelAdmin):
    list_display = ('statusid', 'parent', 'screen_name', 'status_text_tag', 'tweetdj_link', 'status_url_tag',)
    search_fields = ['statusid', 'parent__statusid', 'screen_name',]
    fields = ('statusid', 'parent', 'screen_name', 'status_text_tag', 'tweetdj_link', 'status_url_tag',)
    readonly_fields = ('statusid', 'parent', 'screen_name', 'status_text_tag', 'tweetdj_link', 'status_url_tag',)

    def tweetdj_link(self, obj):
        if Tweetdj.objects.filter(statusid=obj.statusid).exists():
            return mark_safe(
                '<a href="{}">🗃️</a>'
                .format(
                    reverse("admin:conversation_tweetdj_change", args=(obj.statusid,))
                )
            )
        else:
            return "❌"
    
    tweetdj_link.short_description = 'Status'
    
    def screen_name(self, obj):
        return screen_name_link(self,obj)

    screen_name.short_description = "Screen name"

admin.site.register(Treedj, TreedjAdmin)

class HashtagAdmin(admin.ModelAdmin):
    pass

admin.site.register(Hashtag, HashtagAdmin)

