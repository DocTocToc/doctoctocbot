from django.contrib import admin

from .models import Project, ProjectInvestment, Tier

class ProjectInvestmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'email', 'pledged', 'paid', 'datetime', 'public',)

class TierAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'title', 'description', 'emoji', 'min', 'max',)
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Project)
admin.site.register(ProjectInvestment, ProjectInvestmentAdmin)
admin.site.register(Tier, TierAdmin)
