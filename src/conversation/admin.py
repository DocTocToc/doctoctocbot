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

logger = logging.getLogger(__name__)

from .models import Treedj, Tweetdj

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
    list_display = ('statusid', 'userid', 'screen_name_tag', 'status_text_tag', 'status_link', 'hashtag0', 'hashtag1', 'created_at', 'quotedstatus', 'retweetedstatus', 'deleted',)
    search_fields = ['statusid', 'userid', 'json',]
    fields = ('statusid', 'userid', 'screen_name_tag', 'status_text_tag', 'status_url_tag', 'json', 'hashtag0', 'hashtag1', 'created_at', 'quotedstatus', 'retweetedstatus',)
    readonly_fields = ('statusid', 'userid', 'screen_name_tag', 'status_text_tag', 'status_url_tag', 'json', 'created_at', 'quotedstatus', 'retweetedstatus',)
    list_filter = (
        ('created_at', DateTimeRangeFilter),
        'hashtag0',
        'hashtag1',
        'quotedstatus',
        'retweetedstatus',
        'deleted',
        CategoryListFilter,
    )

    def status_link(self, obj):
        return mark_safe('<a href="https://twitter.com/statuses/%s">🐦</a>' % (obj.statusid))

    status_link.short_description = 'tweet'

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
