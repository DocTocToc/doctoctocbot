from django.contrib import admin
from matrix.models import (
    CategoryAccessControl,
    CommunityAccessControl,
    Account,
)

class CategoryAccessControlAdmin(admin.ModelAdmin):
    list_display = (
        'category',
        'authorize',
    )


class CommunityAccessControlAdmin(admin.ModelAdmin):
    list_display = (
        'community',
        'authorize',
    )


class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'user_id',
        'password',
        'access_token',
        'device_id',
        'homeserver',
        'nio_store',
    )
    
admin.site.register(CategoryAccessControl, CategoryAccessControlAdmin)
admin.site.register(CommunityAccessControl, CommunityAccessControlAdmin)
admin.site.register(Account, AccountAdmin)

