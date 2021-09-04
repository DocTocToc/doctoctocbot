import logging
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from moderation.models import SocialUser, SocialMedia
from django.shortcuts import render
from rest_framework.views import APIView
from charts.utils import get_userid_lst, get_user_id, get_bot_id
from bot.lib.datetime import get_datetime_tz_from_twitter_str
from rest_framework.response import Response

logger = logging.getLogger(__name__)

class CreationFollowerChartView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'charts/creation_follower.html')

    
class CreationFollowerChartData(APIView):
    authentication_classes = []
    permission_classes = []
    
    @staticmethod
    def get_data(userid_lst):
        try:
            socmed = SocialMedia.objects.get(name="twitter")
        except SocialMedia.DoesNotExist:
            return
        data = list(
            SocialUser.objects
            .filter(
                user_id__in=userid_lst,
                social_media=socmed,
            )
            .values(
                "profile__json__created_at",
                "profile__json__followers_count",
                "profile__json__screen_name",
                "profile__json__id",)

        )
        logger.debug(f'{len(data)=}')
        for i in range(len(data)):
            try:
                dict = data.pop(i)
            except IndexError:
                continue
            twitter_datetime: str =  dict.pop("profile__json__created_at")
            if not twitter_datetime:
                continue
            python_datetime = get_datetime_tz_from_twitter_str(twitter_datetime)
            dict["x"] = python_datetime.date().isoformat()
            dict["y"] = dict.pop("profile__json__followers_count")
            dict["id"] = dict.pop("profile__json__id")
            dict["screen_name"] = dict.pop("profile__json__screen_name")
            data.insert(i, dict)
        return data

    def get(self, request, format=None):
        res = {
            "data": None,
            "data_bot": None,
            "data_user": None,
        }

        member_userid_lst = get_userid_lst(request)
        data = CreationFollowerChartData.get_data(member_userid_lst)
        res["data"] = data

        user_id = get_user_id(request)
        if user_id:
            data = CreationFollowerChartData.get_data([user_id])
            res["data_user"] = data

        bot_id = get_bot_id(request)
        if bot_id:
            data = CreationFollowerChartData.get_data([bot_id])
            res["data_bot"] = data

        logger.debug(res)
        return Response(res)