from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from moderation.models import SocialUser, SocialMedia
from django.shortcuts import render
from rest_framework.views import APIView
from charts.utils import get_userid_lst
from bot.lib.datetime import get_datetime_tz_from_twitter_str
from rest_framework.response import Response


class CreationFollowerChartView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'charts/creation_follower.html')

    
class CreationFollowerChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        try:
            socmed = SocialMedia.objects.get(name="twitter")
        except SocialMedia.DoesNotExist:
            return
        member_userid_lst = get_userid_lst(request)
        labels = []
        data = list(
            SocialUser.objects
            .filter(
                user_id__in=member_userid_lst,
                social_media=socmed,
            )
            .values(
                "profile__json__created_at",
                "profile__json__followers_count",
                "profile__json__screen_name",)
        )
        for i in range(len(data)):
            dict = data.pop(i)
            twitter_datetime: str =  dict.pop("profile__json__created_at")
            python_datetime = get_datetime_tz_from_twitter_str(twitter_datetime)
            dict["t"] = python_datetime.date().isoformat()
            dict["y"] = dict.pop("profile__json__followers_count")
            labels.insert(i, dict.pop("profile__json__screen_name"))
            data.insert(i, dict)
        res = {
            "labels": labels,
            "data": data,
        }
        return Response(res)