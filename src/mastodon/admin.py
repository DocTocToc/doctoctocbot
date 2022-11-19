from django.contrib import admin
from mastodon.models import MastodonInvitation

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
