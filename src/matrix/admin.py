from django.contrib import admin
from matrix.models import (
    CategoryAccessControl,
    CommunityAccessControl,
    Account,
    FilterSocial,
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


class FilterSocialAdmin(admin.ModelAdmin):
    list_display = (
        'label',
        'active',
        'friend_category_tag',
        'friend_lower',
        'follower_category_tag',
        'follower_lower',
    )


"""
    def friend_category_tag(self, obj):
        return self.friend_category_tag()

    friend_category_tag.short_description = "Friend categories"

    def follower_category_tag(self, obj):
        return follower_category_tag(obj)

    follower_category_tag.short_description = "Follower categories"
"""

admin.site.register(CategoryAccessControl, CategoryAccessControlAdmin)
admin.site.register(CommunityAccessControl, CommunityAccessControlAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(FilterSocial, FilterSocialAdmin)
