from django.contrib import admin

from .models import Project, ProjectInvestor

admin.site.register(Project)
admin.site.register(ProjectInvestor)