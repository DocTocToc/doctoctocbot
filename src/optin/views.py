import logging

from django.shortcuts import render
from django.db.utils import DatabaseError

from rest_framework.decorators import api_view, permission_classes, parser_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from optin.models import OptIn, Option 
from common.drf import ServiceUnavailable

logger = logging.getLogger(__name__)


@api_view(['POST'])
@parser_classes([JSONParser])
@permission_classes([IsAuthenticated])
def get_optin_view(request, format=None):
    if request.method == 'POST':
        socialuser = request.user.socialuser
        logger.debug(socialuser)
        if not socialuser:
            return Response({"authorize": None})
        logger.debug(request.data)
        try:
            option = Option.objects.get(name=request.data.get("option"))
            logger.debug(f"{option}")
        except Option.DoesNotExist:
            return Response({"authorize": None})
        try:
            optin = OptIn.objects.current.get(socialuser=socialuser, option=option)
            authorize = optin.authorize
        except OptIn.DoesNotExist:
            authorize = option.default_bool
        label = option.label
        description = option.description
        response = Response(
            {
                'authorize': authorize,
                'label': label,
                'description': description
            }
        )
        response["Access-Control-Allow-Origin"] = "*"
        return response

@api_view(['POST'])
@parser_classes([JSONParser])
@renderer_classes([JSONRenderer])
@permission_classes([IsAuthenticated])    
def update_optin_view(request, format=None):
    if request.method == 'POST':
        socialuser = request.user.socialuser
        if not socialuser:
            return Response({"authorize": None})
        try:
            option = Option.objects.get(name=request.data["option"])
        except Option.DoesNotExist:
            return Response({"authorize": None})
        try:
            optin = OptIn.objects.current.get(socialuser=socialuser, option=option)
            logger.debug(f"optin: {optin}")
            optin = optin.clone()
            logger.debug(f"cloned optin: {optin}")
        except OptIn.DoesNotExist:
            logger.debug(f"create optin")
            # toggle boolean field
            default_authorize = option.default_bool
            try:
                optin = OptIn.objects.create(
                    socialuser = socialuser,
                    option = option,
                    authorize = default_authorize
                )
            except DatabaseError:
                raise ServiceUnavailable
        authorize = optin.authorize
        if authorize is None:
            optin.authorize = False
        else:
            optin.authorize = not authorize
        optin.save()

        authorize = optin.authorize
        return Response({
            "option": option.name,
            "authorize": authorize,
            })