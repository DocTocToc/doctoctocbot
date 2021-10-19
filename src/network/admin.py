from django.contrib import admin

from network.models import (
    Network,
)


class NetworkCommunityInline(admin.TabularInline):
    model = Network.community.through
    extra = 1
    #raw_id_fields = ("", "",)


@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'label',
        'twitter_account',   
)
    inlines = (NetworkCommunityInline,)


