import logging
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from choice.models import (
    Diploma,
    Discipline,
    Participant,
    ParticipantType,
    Room,
    School,
)
from constance import config
from urllib.parse import quote

logger = logging.getLogger(__name__)

class DiplomaSerializer(serializers.ModelSerializer):


    class Meta:
        model = Diploma
        fields = (
            'id',
            'name',
            'slug',
            'label',
            'discipline',
        )


class SchoolSerializer(serializers.ModelSerializer):


    class Meta:
        model = School
        fields = (
            'tag',
            'slug',
        )


class DisciplineSerializer(serializers.ModelSerializer):


    class Meta:
        model = Discipline
        fields = (
            'id',
            'name',
            'label',
        )


class ParticipantTypeSerializer(serializers.ModelSerializer):


    class Meta:
        model = ParticipantType
        fields = (
            'id',
            'name',
            'slug',
            'label',
        )


class RoomSerializer(serializers.ModelSerializer):
    school = SchoolSerializer
    diploma = DiplomaSerializer
    room_link = serializers.SerializerMethodField()
    active = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = (
            'id',
            'room_id',
            'room_alias',
            'room_link',
            'diploma',
            'school',
            'active',
        )
        depth = 1
 
    def get_room_link(self, obj):
        #cas_url = config.choice_cas_url
        homeserver_url =  config.choice_matrix_homeserver_url
        room_url = config.choice_matrix_room_url
        #next = quote(f"{cas_url}{config.choice_matrix_room_url}{obj.room_alias}:{homeserver_url}", safe='')
        return f"{room_url}{obj.room_alias}:{homeserver_url}"
    
    def get_active(self, obj):
        request = self.context.get('request', None)
        if request:
            user = request.user
        else:
            return
        participant = Participant.objects.get(user=user)
        pr = obj.participantroom_set.get(
            participant=participant
        )
        return pr.active


class ParticipantRoomSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True, many=True)

    class Meta:
        model = Participant
        fields = ('room',)
