from django.contrib import admin
from matrix.models import CategoryAccessControl, CommunityAccessControl

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

admin.site.register(CategoryAccessControl, CategoryAccessControlAdmin)
admin.site.register(CommunityAccessControl, CommunityAccessControlAdmin)
