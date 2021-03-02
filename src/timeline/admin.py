from django.contrib import admin

from .models import Status
from conversation.admin_tags import admin_tag_status_datetime

class StatusAdmin(admin.ModelAdmin):
    list_display = (
        'statusid',
        'status_datetime',
        'status_url_tag',
        'community'
    )
    search_fields = (
        'statusid',
    )
    list_filter = (
        'community',
    )
    fields = (
        'statusid',
        'status_datetime',
        'status_url_tag',
        'json',
        'community',
    )
    readonly_fields = (
        'statusid',
        'status_datetime',
        'status_url_tag',
        'json',
        'community',
    )
    
    def status_datetime(self, obj):
        return admin_tag_status_datetime(obj.statusid)
    
    status_datetime.short_description = 'datetime'
   

admin.site.register(Status, StatusAdmin)