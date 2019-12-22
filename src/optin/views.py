import logging

logger = logging.getLogger(__name__)
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, parser_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from optin.models import OptIn, Option 



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
            return Response({"authorize": None})
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
            optin = optin.clone()
            # toggle boolean field
            authorize = optin.authorize
            if authorize is None:
                authorize = False
            optin.authorize = not authorize
            optin.save()
        except OptIn.DoesNotExist:
            return Response({"authorize": None})
        authorize = optin.authorize
        return Response({
            "option": option.name,
            "authorize": authorize,
            })