from django.contrib import admin
from discourse.models import AccessControl

class AccessControlAdmin(admin.ModelAdmin):
    list_display = (
        'category',
        'authorize',
    )

admin.site.register(AccessControl, AccessControlAdmin)