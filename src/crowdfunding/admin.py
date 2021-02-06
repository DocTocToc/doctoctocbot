from .models import Project, ProjectInvestment, Tier

from django.urls import reverse
from django.contrib import admin
from django.utils.safestring import mark_safe

class ProjectInvestmentAdmin(admin.ModelAdmin):
    empty_value_display = '∅'
    list_display = (
        'uuid',
        'project',
        'user_tag',
        'socialuser_tag',
        'name',
        'email',
        'pledged',
        'paid',
        'datetime',
        'public',
        'invoice',
        'invoice_pdf',
    )
    search_fields = [
        'user__last_name',
        'user__first_name',
        'user__username',
        'user__socialuser__user_id',
        'user__socialuser__profile__json__name',
        'user__socialuser__profile__json__screen_name',
        'name',
        'email',
    ]
    list_filter = [
        'paid',
        'datetime',
        'public',
        'project',
        'invoice_pdf',
    ]
    ordering = ['-datetime',]
    date_hierarchy = 'datetime'
    
    def socialuser_tag(self, obj):
        su = obj.user.socialuser
        if not su:
            return
        url = reverse("admin:moderation_socialuser_change", args=[su.id])
        name = su.screen_name_tag() or obj.user.username
        try:
            emoji = su.social_media.emoji
        except:
            emoji = None
        tag = f"{emoji}{name}"
        return mark_safe(f'<a href="{url}">{tag}</a>')
    socialuser_tag.short_description = "SocialUser"

    def user_tag(self, obj):
        u = obj.user
        if not u:
            return
        url = reverse("admin:users_user_change", args=[u.id])
        return mark_safe(f'<a href="{url}">{u.username}</a>')
    user_tag.short_description = "Django user"


class TierAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'title', 'description', 'emoji', 'min', 'max',)
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Project)
admin.site.register(ProjectInvestment, ProjectInvestmentAdmin)
admin.site.register(Tier, TierAdmin)
