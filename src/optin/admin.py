from django.contrib import admin
from optin.models import OptIn, Option
from versions.admin import VersionedAdmin

class OptInAdmin(VersionedAdmin):
    list_display = (
        'option',
        'socialuser',
        'authorize',    
    )
    search_fields = (
        'socialuser__profile__json',
    )
    list_filter = (
        'option__label',
        'authorize',
    )
    autocomplete_fields = ['socialuser']
    list_display_show_identity = False
    list_display_show_end_date = True
    list_display_show_start_date = True


admin.site.register(OptIn, OptInAdmin)
admin.site.register(Option)