from django.contrib import admin
from fediverse.models import (
    MastodonInvitation,
    MastodonScopes,
    MastodonApp,
    MastodonAccess,
    Toot,
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
        'scopes_tag',
        'api_base_url',
        'client_id',
        'client_secret',
        'website',
        'redirect_uris',
        'created'
    ]

    def scopes_tag(self, obj):
        return [s.scope for s in obj.scopes.all()]

    scopes_tag.short_description = 'scopes'


@admin.register(MastodonAccess)
class MastodonAccessAdmin(admin.ModelAdmin):
    list_display = (
        'app',
        'user',
        'access_token',
    )
    search_fields = (
        'user__acct',
    )
    list_filter = (
        'app',
    )


@admin.register(Toot)
class Toot(admin.ModelAdmin):
    list_display = (
        'user',
        'uri_id',
        'db_id',
        'created_at',
        'edited_at',
        'in_reply_to_id',
        'in_reply_to_account_id',
        'hashtag_tag',
        'reblogged_by_tag',
        'created',
        'updated',
    )
    fields = (
        'user',
        'uri_id',
        'db_id',
        'created_at',
        'edited_at',
        'in_reply_to_id',
        'in_reply_to_account_id',
        'hashtag_tag',
        'reblogged_by_tag',
        'status',
        'created',
        'updated',
    )
    readonly_fields = (
        'user',
        'uri_id',
        'db_id',
        'created_at',
        'edited_at',
        'in_reply_to_id',
        'in_reply_to_account_id',
        'hashtag_tag',
        'reblogged_by_tag',
        'status',
        'created',
        'updated',
    )

    def hashtag_tag(self, obj):
        return ",".join(
            [h.hashtag for h in obj.hashtag.all()]
        )

    hashtag_tag.short_description = 'hashtag'

    def reblogged_by_tag(self, obj):
        return ",".join(
            [r.acct for r in obj.reblogged_by.all()]
        )

    reblogged_by_tag.short_description = 'reblogged by'