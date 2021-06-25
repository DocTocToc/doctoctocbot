from django.contrib import admin
from choice.models import School
from leaflet.admin import LeafletGeoAdmin

@admin.register(School)
class LocationAdmin(LeafletGeoAdmin):
    list_display = ("id", "tag", "name", "university",)
    settings_overrides = {
       'DEFAULT_CENTER': (49.474182, 10.988509),
       'DEFAULT_ZOOM': 15,
    }
    display_raw = True
