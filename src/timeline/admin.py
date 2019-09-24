from django.contrib import admin

from .models import Status

class StatusAdmin(admin.ModelAdmin):
    list_display = ('statusid', 'status_url_tag', 'community')
    search_fields = ['statusid',]
    fields = ('statusid', 'status_url_tag', 'json', 'community',)
    readonly_fields = ('statusid', 'status_url_tag', 'json', 'community',)

admin.site.register(Status, StatusAdmin)