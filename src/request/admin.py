from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils.html import format_html

from versions.admin import VersionedAdmin
from moderation.models import SocialUser, UserCategoryRelationship
from request.models import Queue
from django.db.models import F
from django.utils.translation import ugettext_lazy as _

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
    list_display = (
        'mini_image_tag',
        'screen_name_link',
        'state_tag',
        'uid',
        'socialuser',
        'community',
        'category_tag',
        'socialmedia',
    )
    list_filter = (
        'state',
        'community',
        'socialmedia',
        isSelfVerified,
        'socialuser__category__name',
    )
    readonly_fields = (
        'mini_image_tag',
        'screen_name_link',
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
        try:
            su = SocialUser.objects.get(user_id=obj.uid)
            return mark_safe(
                '<a href="{link}">{tag}</a>'.format(
                    link = reverse("admin:moderation_socialuser_change", args=(su.pk,)),
                    tag = obj.socialuser.screen_name_tag()
                )
            )
        except SocialUser.DoesNotExist:
            return obj.socialuser.screen_name_tag()
    
    screen_name_link.short_description = 'Screen name'
    
    def mini_image_tag(self, obj):
        from django.contrib.staticfiles.templatetags.staticfiles import static
        p = obj.socialuser.profile
        if p:
            url = p.miniavatar.url
        else:
            url = static("moderation/twitter_unknown_images/egg24x24.png")
        
        return mark_safe('<img src="%s"/>' % url)
    
    mini_image_tag.short_description = 'Image'

    def category_tag(self, obj):
        category_lst = ["<ul>"]
        for relation in obj.socialuser.categoryrelationships.all():
            try:
                screen_name = relation.moderator.screen_name_tag()
            except:
                screen_name = ""
            try:
                category = relation.category.name
            except:
                category = ""
            if category:
                category_lst.append(
                    f"<li>{category} - "
                    f"{screen_name}</li>"
                )
        category_lst.append("</ul>")
        return format_html("".join(category_lst))
    
    category_tag.short_description = _('Categories')

    def get_ordering(self, request):
        return ['-version_start_date']


admin.site.register(Queue, QueueAdmin)