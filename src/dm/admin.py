from django.contrib import admin

from .models import DirectMessage


class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_timestamp', 'sender_id', 'recipient_id', 'text',)
    fields = ('id', 'created_timestamp', 'sender_id', 'recipient_id', 'text', 'jsn',)
    readonly_fields = ('recipient_id',)


admin.site.register(DirectMessage, DirectMessageAdmin)