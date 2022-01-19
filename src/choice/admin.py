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
from choice.utils import room_url
from django.utils.html import mark_safe
from leaflet.admin import LeafletGeoAdmin


@admin.register(School)
class LocationAdmin(LeafletGeoAdmin):
    list_display = (
        "id",
        "tag",
        "slug",
        "name",
        "university",
        "active",
    )
    settings_overrides = {
       'DEFAULT_CENTER': (48.853329, 2.348851),
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
        "room_tag",
    )
    inlines = (ParticipantRoomInline,)
    
    def room_tag(self, obj):
        def room_link(room):
            return (
                f'<a href="{room_url(room)}">{room.diploma} | {room.school}</a>'
            )
        rooms = [f"{room_link(room)}" for room in obj.room.filter(participantroom__active=True)]
        return mark_safe(
            ", ".join(rooms)
        )

    room_tag.short_description = "Rooms"

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