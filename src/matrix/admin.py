from django.contrib import admin
from matrix.models import CategoryAccessControl

class CategoryAccessControlAdmin(admin.ModelAdmin):
    list_display = (
        'category',
        'authorize',
    )

admin.site.register(CategoryAccessControl, CategoryAccessControlAdmin)
