from django.contrib import admin
from messenger.models import (
    Message,
    Campaign,
    Receipt,
    CampaignMessage
)

class CampaignMessageInline(admin.TabularInline):
    model = CampaignMessage
    extra = 1

class CampaignAdmin(admin.ModelAdmin):
    inlines = (CampaignMessageInline,)



admin.site.register(Message)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(Receipt)