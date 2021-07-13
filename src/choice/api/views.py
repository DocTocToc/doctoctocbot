import logging

from choice.models import (
    Diploma,
    School,
    Discipline,
    Participant,
    ParticipantType,
    ParticipantRoom,
    Room,
)
from choice.api import serializers
from choice.matrix import CreateRoomSync
from rest_framework import viewsets
from rest_framework.decorators import (
    api_view,
    permission_classes,
    parser_classes,
    renderer_classes,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import bad_request, server_error
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)

@permission_classes([AllowAny])
class DiplomaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing diplomas.
    """
    queryset = Diploma.objects.all()
    serializer_class = serializers.DiplomaSerializer


@permission_classes([AllowAny])
class DisciplineViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing disciplines.
    """
    queryset = Discipline.objects.all()
    serializer_class = serializers.DisciplineSerializer
    
@permission_classes([AllowAny])
class ParticipantTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing participants.
    """
    queryset = ParticipantType.objects.all()
    serializer_class = serializers.ParticipantTypeSerializer


@permission_classes([IsAuthenticated])#@permission_classes([AllowAny])
class CreateRoom(APIView):
    """
    View to create a new room.

    * Requires token authentication.
    * Only authenticated users are able to access this view.
    """
    #authentication_classes = [authentication.TokenAuthentication]
    #permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        pt_slug: str = kwargs.get('role', None)
        school_slug: str = kwargs.get('school', None)
        diploma_slug: str = kwargs.get('diploma', None)
        try:
            pt: ParticipantType = ParticipantType.objects.get(slug=pt_slug) 
        except ParticipantType.DoesNotExist:
            return bad_request(request)
        try:
            school: School = School.objects.get(slug=school_slug)
        except School.DoesNotExist:
            return bad_request(request)
        try:
            diploma: Diploma = Diploma.objects.get(slug=diploma_slug)
        except Diploma.DoesNotExist:
            return bad_request(request)
        try:
            room = Room.objects.get(diploma=diploma, school=school)
        except Room.DoesNotExist:
            cr = CreateRoomSync(diploma=diploma, school=school)
            logger.debug(cr)
            resp = cr.create()
            if resp:
                try:
                    room = Room.objects.create(
                        school=school,
                        diploma=diploma,
                        room_id=resp,
                        room_alias=cr.room_alias,
                    )
                except:
                    return server_error(request)
        user = request.user
        if user == AnonymousUser:
            return server_error(request)
        participant, _created = Participant.objects.get_or_create(
            user=user,
            type=pt,
        )
        if not participant:
            return server_error(request)
        if room in participant.room.all():
            pr = ParticipantRoom.objects.get(
                participant=participant,
                room=room,
            )
            pr.active=True
            pr.save()
        else:
            participant.room.add(room)
        return Response(
            {
                "school": room.school.slug,
                "diploma": room.diploma.slug,
                "room_id": room.room_id,
                "room_alias": room.room_alias, 
            }
        )

@permission_classes([IsAuthenticated])#@permission_classes([AllowAny])
class InactivateRoom(APIView):
    """
    View to make existing room inactive for user.

    * Requires token authentication.
    * Only authenticated users are able to access this view.
    """
    #authentication_classes = [authentication.TokenAuthentication]
    #permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        school_slug: str = kwargs.get('school', None)
        diploma_slug: str = kwargs.get('diploma', None)
        try:
            school: School = School.objects.get(slug=school_slug)
        except School.DoesNotExist:
            return bad_request(request)
        try:
            diploma: Diploma = Diploma.objects.get(slug=diploma_slug)
        except Diploma.DoesNotExist:
            return bad_request(request)
        try:
            room = Room.objects.get(diploma=diploma, school=school)
        except Room.DoesNotExist:
            return bad_request(request)
        user = request.user
        if user == AnonymousUser:
            return server_error(request)
        try:
            participant = Participant.objects.get(user=user)
        except Participant.DoesNotExist:
            return server_error(request)
        try:
            pr= ParticipantRoom.objects.get(
                participant=participant,
                room=room
            )
        except ParticipantRoom.DoesNotExist:
            return server_error(request)
        pr.active=False
        pr.save()
        return Response(None, status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
class ParticipantRoomViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing diplomas.
    """
    queryset = Participant.objects.all()
    serializer_class = serializers.ParticipantRoomSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)