from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils.html import format_html

from versions.admin import VersionedAdmin
from moderation.models import SocialUser, UserCategoryRelationship
from request.models import Queue, RequestStatus
from moderation.admin_tags import (
    admin_tag_category,
    screen_name_link_su
)
from django.templatetags.static import static
from django.db.models import F
from django.utils.translation import ugettext_lazy as _
from common.list_filter import by_socialuser_category_filter


class isSelfVerified(admin.SimpleListFilter):
    title = 'Self verified'
    parameter_name = 'is_self_verified'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'yes':
            return queryset.filter(
                socialuser__categoryrelationships__moderator__pk=F(
                    'socialuser__pk'
                )
            )
        elif value == 'no':
            pks = UserCategoryRelationship.objects \
                .filter(social_user=F('moderator')) \
                .values_list('social_user__pk', flat=True)
            return queryset.exclude(
                socialuser__pk__in=pks
            )
        return queryset

class QueueAdmin(VersionedAdmin):
    empty_value_display = '∅'
    list_display = (
        'mini_image_tag',
        'screen_name_link',
        'state_tag',
        'dm_tag',
        'uid',
        'community',
        'category_tag',
        'socialmedia',
    )
    list_filter = (
        'state',
        'community',
        'socialmedia',
        isSelfVerified,
        by_socialuser_category_filter('socialuser__category', 'Category'),
    )
    readonly_fields = (
        'mini_image_tag',
        'screen_name_link',
        'state_tag',
        'dm_tag',
        'uid',
        'socialuser',
        'community',
        'socialmedia',   
    )
    search_fields = (
        'socialuser__profile__json__screen_name',
    )
    list_display_show_identity = False
    list_display_show_end_date = True
    list_display_show_start_date = True

    def state_tag(self, obj):
        if obj.state == Queue.PENDING:
            return "pending⌛"
        else:
            return obj.state

    state_tag.short_description = 'STATE'

    def screen_name_link(self, obj):
        return screen_name_link_su(obj)

    screen_name_link.short_description = 'Screen name'

    def mini_image_tag(self, obj):
        p = obj.socialuser.profile
        if p:
            url = p.miniavatar.url
        else:
            url = static("moderation/twitter_unknown_images/egg24x24.png")

        return mark_safe('<img src="%s"/>' % url)

    mini_image_tag.short_description = 'Image'

    def category_tag(self, obj):
        return admin_tag_category(obj.socialuser)

    category_tag.short_description = _('Categories')

    def dm_tag(self, obj):
        if not obj.requestdm:
            return
        if obj.requestdm.state == "F":
            return "❌"
        else:
            return "✔️"

    dm_tag.short_description = "DM"

    def get_ordering(self, request):
        return ['-version_start_date']


@admin.register(RequestStatus)
class RequestStatusAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'queue',
        'status',
    )


admin.site.register(Queue, QueueAdmin)