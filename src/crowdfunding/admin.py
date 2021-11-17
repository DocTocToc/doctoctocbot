from .models import (
    Project,
    Campaign,
    ProjectInvestment,
    Tier,
    PaymentProcessorWebhook
)

from django.urls import reverse
from django.contrib import admin
from django.utils.safestring import mark_safe

class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
        'provider',
        'product',
        'currency',
    )


class CampaignAdmin(admin.ModelAdmin):
    list_display = (
        'project',
        'start_datetime',
        'end_datetime',
        'goal',
    )


class ProjectInvestmentAdmin(admin.ModelAdmin):
    empty_value_display = '∅'
    list_display = (
        'uuid',
        'project',
        'campaign',
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
    readonly_fields = (
        'payment_intent',
        'datetime',
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
        'campaign',
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


class PaymentProcessorWebhookAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'site',
        'secret_tag'
    )

    def secret_tag(self, obj):
        secret = obj.secret
        if not secret:
            return
        return "*" * len(secret)

    secret_tag.short_description = "Secret"

admin.site.register(Project, ProjectAdmin)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(ProjectInvestment, ProjectInvestmentAdmin)
admin.site.register(Tier, TierAdmin)
admin.site.register(PaymentProcessorWebhook, PaymentProcessorWebhookAdmin)