from django.contrib import admin
from twttr.models import UserActive

@admin.register(UserActive)
class UserActiveAdmin(admin.ModelAdmin):
    list_display = [
        'active',
        'socialuser',
        'created',
    ]
    