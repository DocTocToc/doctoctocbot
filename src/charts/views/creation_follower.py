import logging
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from moderation.models import SocialUser, SocialMedia, Follower
from django.shortcuts import render
from rest_framework.views import APIView
from charts.utils import get_userid_lst, get_twitter_user_id, get_bot_id
from bot.lib.datetime import get_datetime_tz_from_twitter_str
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext as _
import webcolors
from django.db import models
from bot.tweepy_api import gen_api
from moderation.social import update_social_ids
from community.helpers import get_community
from community.models import CommunityCategoryRelationship
from django.core.cache import cache
from conversation.models import TwitterLanguageIdentifier
from django.conf import settings
from constance import config

logger = logging.getLogger(__name__)

"""
label: 'All followers',
                      backgroundColor: color(window.chartColors.grey).alpha(0.6).rgbString(),
                      borderColor: window.chartColors.grey,
                      data: data.data_all
"""

def rgb_to_rgba(color_name, alpha):
    """
    Adds the alpha channel to an RGB Value and returns it as an RGBA Value
    :param rgb_value: Input RGB Value
    :param alpha: Alpha Value to add  in range [0,1]
    :return: RGBA Value
    """
    iRGB=webcolors.name_to_rgb(color_name)
    return f"rgba({iRGB.red},{iRGB.green}, {iRGB.blue}, {alpha})"


class ArrayLength(models.Func):
    function = 'CARDINALITY'
        
    
class CreationFollowerChartView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'charts/creation_follower.html')


class CreationFollowerChartData(APIView):
    permission_classes = [IsAuthenticated]

    def get_twitteruserid_list(self)->[int]:
        try:
            tli = TwitterLanguageIdentifier.objects.get(
                tag=self.community.language
            )
        except TwitterLanguageIdentifier.DoesNotExist:
            tli=None
        logger.debug(f'in get_twitteruserid_list: {self.request=}')
        twitteruserid_list = get_userid_lst(self.request,lang=tli)
        if settings.DEBUG:
            twitteruserid_list=twitteruserid_list[:]
        return twitteruserid_list

    def follower_count(self, user_id, category=None):
        if settings.DEBUG:
            TTL=300
        else:
            TTL=config.creation_follower_follower_count_ttl
        if category:
            cache_key=f'follower_count_{user_id}_{category.name}'
        else:
            cache_key=f'follower_count_{user_id}_all'
        count=cache.get(cache_key)
        if not count is None:
            return count
        if not category:
            try:
                count = len(
                    Follower.objects
                    .filter(user__id=user_id)
                    .latest('id')
                    .id_list
                )
                if count:
                    cache.set(
                        f'follower_count_{user_id}_all',
                        count,
                        TTL
                    )
                return count
            except Follower.DoesNotExist:
                try:
                    count = (
                        SocialUser.objects.get(user_id=user_id)
                        .profile.json["followers_count"]
                    )
                except:
                    count = 0
                return count
        members = category.twitter_id_list()
        try:
            followers = (
                Follower.objects
                .filter(user__user_id=user_id)
                .latest('id').id_list
            )
        except Follower.DoesNotExist:
            followers = []
        count = len([e for e in members if e in followers])
        if count:
            cache.set(
                f'follower_count_{user_id}_{category.name}',
                count,
                TTL
            )
        return count

    def datasets(self):
        if settings.DEBUG:
            TTL=30
        else:
            TTL=config.creation_follower_datasets_ttl
        cache_key=f'datasets_{self.community.name}'
        datasets = cache.get(cache_key)
        if datasets:
            return datasets
        datasets = []
        dataset_all = {
            'label': _('All followers'),
            'backgroundColor': rgb_to_rgba("grey", alpha=0.4),
            'borderColor': 'grey',
            'data': self.get_data(),
            'pointRadius': self.get_pointRadius(),
            'pointStyle': self.get_pointStyle()
        }
        datasets.append(dataset_all)
        cats: [dict] = [
            {"cat_obj":ccr.category, "cat_color":ccr.color} for ccr
            in CommunityCategoryRelationship.objects.filter(
                community=self.community,
                follower_chart=True,
            )
        ]
        logger.debug(f'{cats=}')
        for cat in cats:
            label = cat["cat_obj"].label
            color = cat["cat_color"]
            category=cat["cat_obj"]
            logger.debug(f'{category=}')
            cat_data_set = {
                'label': label,
                'backgroundColor': rgb_to_rgba(color, alpha=0.4),
                'borderColor': color,
                'data': self.get_data(category=category),
                'hidden':  (
                    False if (category in self.community.membership.all())
                    else True
                ),
                'pointRadius': self.get_pointRadius(),
                'pointStyle': self.get_pointStyle()
            }
            datasets.append(cat_data_set)
        cache.set(cache_key,datasets,TTL)
        return datasets

    def get_pointStyle(self)->[str]:
        bot_idx=self.twitteruserid_list.index(self.bot_twitteruserid)
        user_idx=self.twitteruserid_list.index(self.twitteruserid)
        lst=["circle"]*len(self.twitteruserid_list)
        lst.pop(bot_idx)
        lst.insert(bot_idx, "triangle")
        lst.pop(user_idx)
        lst.insert(user_idx, "rect")
        return lst
    
    def get_pointRadius(self)->[int]:
        def_rad=3
        bot_rad=12
        user_rad=12
        bot_idx=self.twitteruserid_list.index(self.bot_twitteruserid)
        user_idx=self.twitteruserid_list.index(self.twitteruserid)
        lst=[def_rad]*len(self.twitteruserid_list)
        lst.pop(bot_idx)
        lst.insert(bot_idx, bot_rad)
        lst.pop(user_idx)
        lst.insert(user_idx, user_rad)
        return lst

    def get_data(self, category=None):
        try:
            socmed = SocialMedia.objects.get(name="twitter")
        except SocialMedia.DoesNotExist:
            return
        data = list(
            SocialUser.objects
            .filter(
                user_id__in=self.twitteruserid_list,
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
                dct = data.pop(i)
            except IndexError:
                continue
            twitter_datetime: str =  dct.pop("profile__json__created_at")
            if not twitter_datetime:
                continue
            python_datetime = get_datetime_tz_from_twitter_str(twitter_datetime)
            dct["x"] = python_datetime.date().isoformat()
            user_id = dct.pop("profile__json__id")
            dct["y"] = self.follower_count(user_id, category=category)
            dct["id"] = user_id
            dct["screen_name"] = dct.pop("profile__json__screen_name")
            data.insert(i, dct)
        return data

    def get(self, request, format=None):
        if not request.user.is_authenticated:
            res = {
                "title": _(
                    "You must be authenticted to see this chart."
                ),
                "datasets": []
            }
            return Response(res)
        self.request=request
        logger.debug(self.request)
        self.community=get_community(request)
        self.twitteruserid = get_twitter_user_id(request)
        self.bot_twitteruserid = get_bot_id(request)
        self.twitteruserid_list=self.get_twitteruserid_list()
        if self.bot_twitteruserid:
            self.twitteruserid_list.append(self.bot_twitteruserid)
        if (
            self.twitteruserid
            and
            (not self.twitteruserid in self.twitteruserid_list)
        ):
            self.twitteruserid_list.append(self.twitteruserid)
        self.twitteruserid_list.sort()
        datasets = self.datasets()
        for dct in datasets:
            logger.debug(
                f'{type(dct)=}\n{len(dct)}\n{dct["data"][:20]}\n\n'
            )
        res = {
            "title": _(
                "Follower count (total and by category) vs. creation date of "
                "the account. [■ is you, ▲ is the bot]"
            ),
            "datasets": datasets
        }
        logger.debug(f'{type(res)=}')
        logger.debug(f'{len(res)=}')
        return Response(res)