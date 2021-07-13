from django.contrib import admin
from choice.models import (
    School,
    Discipline,
    Diploma,
    Room,
    Participant,
    ParticipantType,
    ParticipantRoom,
    Text
)
from leaflet.admin import LeafletGeoAdmin

@admin.register(School)
class LocationAdmin(LeafletGeoAdmin):
    list_display = ("id", "tag", "slug", "name", "university",)
    settings_overrides = {
       'DEFAULT_CENTER': (49.474182, 10.988509),
       'DEFAULT_ZOOM': 15,
    }
    display_raw = True


@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ("id", "label", "slug", "name",)


@admin.register(Diploma)
class DiplomaAdmin(admin.ModelAdmin):
    list_display = ("id", "label", "slug", "name", "discipline",)
    list_filter = ("discipline",)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "school",
        "diploma",
        "room_alias",
        "room_id",
    )


class ParticipantRoomInline(admin.TabularInline):
    model = ParticipantRoom
    extra = 1


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "type",
    )
    inlines = (ParticipantRoomInline,)


@admin.register(ParticipantType)
class ParticipantTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
        "label",
    )


@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "label",
        "description",
        "content",
    )