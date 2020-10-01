from django.contrib import admin

from .models import Project, ProjectInvestment, Tier

class ProjectInvestmentAdmin(admin.ModelAdmin):
    list_display = (
        'uuid',
        'project',
        'user',
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
    list_filter = ['paid', 'datetime', 'public',]
    ordering = ['-datetime',]
    date_hierarchy = 'datetime'

class TierAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'title', 'description', 'emoji', 'min', 'max',)
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Project)
admin.site.register(ProjectInvestment, ProjectInvestmentAdmin)
admin.site.register(Tier, TierAdmin)
