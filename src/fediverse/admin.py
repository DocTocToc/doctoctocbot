from django.contrib import admin
from fediverse.models import (
    MastodonInvitation,
    MastodonScopes,
    MastodonApp,
)

@admin.register(MastodonInvitation)
class MastodonInvitationAdmin(admin.ModelAdmin):
    list_display = [
        'uid',
        'socialuser',
        'autofollow',
    ]
    search_fields = (
        'socialuser__profile__json',
        'uid',
        'autofollow_acct',
    )
    raw_id_fields = (
        'socialuser',
        'autofollow',
    )


@admin.register(MastodonScopes)
class MastodonScopesAdmin(admin.ModelAdmin):
    list_display = [
        'scope',
        'description',
        'parent',
    ]
    fields = [
        'scope',
        'description',
        'parent',
    ]


@admin.register(MastodonApp)
class MastodonAppAdmin(admin.ModelAdmin):
    list_display = [
        'client_name',
        'api_base_url',
        'client_id',
        'client_secret',
        'website',
        'redirect_uris',
        'created'
    ]