from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from conversation.models import Treedj, Tweetdj
from django.shortcuts import render
from rest_framework.views import APIView
from charts.utils import get_userid_lst
from bot.lib.datetime import get_datetime_tz_from_twitter_str
from rest_framework.response import Response
from community.helpers import get_community
from community.helpers import get_community_bot_socialuser

import logging

logger = logging.getLogger(__name__)

def reply_delay_data(su):
    data = []
    labels = []
    pks = (
        Tweetdj.objects
        .filter(retweeted_by=su)
        .values_list("statusid", flat=True)
    )
    for pk in pks:
        try:
            root = Treedj.objects.get(statusid=pk)
        except Treedj.DoesNotExist:
            continue
        try:
            root_tweetdj = Tweetdj.objects.get(statusid=pk)
            root_user_id = root_tweetdj.userid
        except Tweetdj.DoesNotExist:
            continue
        labels.append(
            f"@{root_tweetdj.screen_name_tag()}\n"
            f"{root_tweetdj.status_text_tag()}"
        )
        t0 = (root.statusid >> 22) + 1288834974657
        data.append({"x": t0, "y": 0})
        tree =  root.get_descendants(include_self=False)
        for node in tree:
            try:
                tweetdj = Tweetdj.objects.get(statusid=node.statusid)
                user_id = tweetdj.userid
            except Tweetdj.DoesNotExist:
                continue
            # exclude status written by question's author from replies
            if user_id == root_user_id:
                continue
            delta =  ((node.statusid >> 22) + 1288834974657) - t0
            data.append({"x": t0, "y": delta})
            labels.append(
                f"@{tweetdj.screen_name_tag()} "
                f"{tweetdj.status_text_tag()[0:100]}"
            )
            logger.debug(labels)
    return {"labels": labels, "data": data}

class ReplyDelayChartView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'charts/reply_delay.html')

    
class ReplyDelayChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        community = get_community(self.request)
        if not community:
            return
        su = get_community_bot_socialuser(community)
        if not su:
            return
        res = reply_delay_data(su)
        return Response(res)