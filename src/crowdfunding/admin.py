from django.contrib import admin

from .models import Project, ProjectInvestment

class ProjectInvestmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'email', 'pledged', 'paid', 'datetime', 'public',)

admin.site.register(Project)
admin.site.register(ProjectInvestment, ProjectInvestmentAdmin)
