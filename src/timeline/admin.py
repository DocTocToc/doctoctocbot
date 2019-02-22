from django.contrib import admin

from .models import Status

class StatusAdmin(admin.ModelAdmin):
    list_display = ('statusid', 'status_url_tag',)
    search_fields = ['statusid',]
    fields = ('statusid', 'status_url_tag', 'json',)
    readonly_fields = ('statusid', 'status_url_tag', 'json',)

admin.site.register(Status, StatusAdmin)