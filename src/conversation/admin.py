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
from bot.models import Account
from common.twitter import status_url_from_id
from django.db.models.aggregates import Sum, Count

from versions.admin import VersionedAdmin

from constance import config

logger = logging.getLogger(__name__)

from .models import (
    Treedj,
    Tweetdj,
    Hashtag,
    Retweeted,
    TwitterUserTimeline,
    TwitterLanguageIdentifier,
)


def screen_name_link(self, obj):
    try:
        screen_name = obj.json["user"]["screen_name"]
    except (AttributeError, KeyError, TypeError) as _e:
        return
    try:
        return mark_safe(
            '<a href="{link}">{name}</a>'
            .format(
                link=reverse(
                    "admin:moderation_socialuser_change",
                    args=(obj.socialuser.pk,)
                ),
                name=screen_name
            )
        )
    except AttributeError:
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

class LanguageListFilter(admin.SimpleListFilter):

    title = _('Language')

    parameter_name = 'language'

    def lookups(self, request, model_admin):
        lst = list(TwitterLanguageIdentifier.objects.all().values_list('tag', 'language'))
        if hasattr(settings, "SORTING_LOCALE"):
            pool = Pool()
            return pool.apply(localized_tuple_list_sort, [lst, 1, settings.SORTING_LOCALE])
        else:
            return localized_tuple_list_sort(lst, 1)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(json__lang=self.value())
        else:
            return queryset


class RetweetedByListFilter(admin.SimpleListFilter):
    title = _('retweeted by')
    parameter_name = 'retweeted_by'
    
    def lookups(self, request, model_admin):
        account_id: List[int] = list(
            Account.objects.values_list('userid', flat=True)
        )
        return (
            [(str(su.user_id), su.screen_name_tag(),)
            for su in SocialUser.objects.filter(user_id__in=account_id)]
        )
    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(
            retweeted_by=SocialUser.objects.get(user_id=int(self.value()))
        )

class TweetdjAdmin(admin.ModelAdmin):
    list_per_page = config.conversation__admin__tweetdj_list_per_page
    list_display = (
        'statusid',
        'userid',
        'screen_name',
        'status_text_tag',
        'status_link',
        'created_at',
        'quotedstatus',
        'retweetedstatus',
        'deleted',
        'tag_list',
        'retweeted_by_screen_name',
        'rt_by_count',
        'quoted_by_screen_name',
        'qt_by_count',
    )
    search_fields = ['json__text',]
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
        'retweeted_by',
        'rt_by_count',
        'quoted_by',
        'qt_by_count',
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
        'rt_by_count',
        'quoted_by',
        'qt_by_count',
    )
    list_filter = (
        ('created_at', DateTimeRangeFilter),
        'quotedstatus',
        'retweetedstatus',
        'deleted',
        CategoryListFilter,
        'hashtag',
        'tags',
        RetweetedByListFilter,
        LanguageListFilter,
    )
    filter_horizontal = ('retweeted_by',)

    def get_queryset(self, request):
        return Tweetdj.objects.annotate(
            rt_by_cnt=Count('retweeted_by'),
            qt_by_cnt=Count('quoted_by')
        )

    def rt_by_count(self, obj):
        return obj.retweeted_by.all().count()
    
    rt_by_count.short_description = "RT by count"
    
    rt_by_count.admin_order_field = 'rt_by_cnt'
    
    def qt_by_count(self, obj):
        return obj.quoted_by.all().count()
    
    qt_by_count.short_description = "QT by count"
    
    qt_by_count.admin_order_field = 'qt_by_cnt'
    
    def screen_name(self, obj):
        return screen_name_link(self,obj)

    screen_name.short_description = "Screen name"

    def status_link(self, obj):
        return mark_safe(f'<a href="{status_url_from_id(obj.statusid)}">🐦</a>')

    status_link.short_description = 'tweet'

    #def get_queryset(self, request):
    #    return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())

    tag_list.short_description = 'tag'
    
    def retweeted_by_screen_name(self, obj):
        rtby_lst = []
        for rtby in obj.retweeted_by.all():
            snt = rtby.screen_name_tag()
            if snt:
                rtby_lst.append(snt)
        return "\n".join(rtby_lst)
            

    retweeted_by_screen_name.short_description = "RT by"

    def quoted_by_screen_name(self, obj):
        qtby_lst = []
        for qtby in obj.quoted_by.all():
            snt = qtby.screen_name_tag()
            if snt:
                qtby_lst.append(snt)
        return "\n".join(qtby_lst)
            

    quoted_by_screen_name.short_description = "QT by"

admin.site.register(Tweetdj, TweetdjAdmin)


class TreedjAdmin(MPTTModelAdmin):
    list_display = ('statusid', 'parent', 'screen_name', 'status_text_tag', 'tweetdj_link', 'status_url_tag',)
    search_fields = ['statusid', 'parent__statusid',]
    fields = ('statusid', 'parent', 'screen_name', 'status_text_tag', 'tweetdj_link', 'status_url_tag',)
    readonly_fields = ('statusid', 'parent', 'screen_name', 'status_text_tag', 'tweetdj_link', 'status_url_tag',)
    ordering = ('-statusid',)

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



class RetweetedAdmin(VersionedAdmin):
    list_display = (
        'status',
        'status_link',
        'retweet',
        'account',  
    )
    fields = (
        'status',
        'status_link',
        'retweet',
        'account',
    )
    readonly_fields = (
        'status',
        'status_link',
        'retweet',
        'account',   
    )
    list_display_show_identity = True
    list_display_show_end_date = True
    list_display_show_start_date = True
    
    def status_link(self, obj):
        return mark_safe(f'<a href="{status_url_from_id(obj.status)}">🐦</a>')

    status_link.short_description = 'status'


class HashtagAdmin(admin.ModelAdmin):
    pass

class TwitterUserTimelineAdmin(admin.ModelAdmin):
    list_display = (
        'userid',
        'screen_name_tag',
        'created_at',
        'last_api_call',
        'statusid_updated_at',
        'statusid',
    )
    def screen_name_tag(self, obj):
        try:
            return SocialUser.objects.get(user_id=obj.userid).screen_name_tag()
        except SocialUser.DoesNotExist:
            return

    screen_name_tag.short_description = 'Screen name'

class TwitterLanguageIdentifierAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'language',
        'tag',    
    )
    readonly_fields = (
        'id',
        'tag',
        'language',
    )
    search_fields = [
        'language',
        'tag',    
    ]


admin.site.register(Treedj, TreedjAdmin)
admin.site.register(Hashtag, HashtagAdmin)
admin.site.register(Retweeted, RetweetedAdmin)
admin.site.register(TwitterUserTimeline, TwitterUserTimelineAdmin)
admin.site.register(TwitterLanguageIdentifier, TwitterLanguageIdentifierAdmin)