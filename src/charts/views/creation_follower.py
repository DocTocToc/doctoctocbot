import logging
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from moderation.models import SocialUser, SocialMedia, Follower
from django.shortcuts import render
from rest_framework.views import APIView
from charts.utils import get_userid_lst, get_user_id, get_bot_id
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

    @staticmethod
    def follower_count(user_id, category=None):
        if settings.DEBUG:
            TTL=30
        else:
            TTL=config.creation_follower_follower_count_ttl
        if category:
            cache_key=f'follower_count_{user_id}_{category.name}'
        else:
            cache_key=f'follower_count_{user_id}_all'
        count=cache.get(cache_key)
        if not count is None:
            return count
        #api_gen = gen_api()
        if not category:
            try:
                count = len(
                    Follower.objects
                    .filter(user__id=user_id)
                    .latest('id')
                    .id_list
                )
                if count:
                    cache.set(f'follower_count_{user_id}_all', count, TTL)
                return count
            except Follower.DoesNotExist:
                """
                api=next(api_gen)
                update_social_ids(
                    user_id,
                    relationship='followers',
                    api=api
                )
                """
                try:
                    count = SocialUser.objects.get(user_id=user_id).profile.json["followers_count"]
                except:
                    count = 0
                return count
        members = category.twitter_id_list()
        logger.debug(f'{len(members)=}')
        try:
            followers = Follower.objects.filter(user__id=user_id).latest('id').id_list
        except Follower.DoesNotExist:
            followers = []
        logger.debug(f'{len(followers)}')
        count = len([e for e in members if e in followers])
        if count:
            cache.set(f'follower_count_{user_id}_{category.name}', count, TTL)
        return count

    @staticmethod
    def datasets(request):
        if settings.DEBUG:
            TTL=30
        else:
            TTL=config.creation_follower_datasets_ttl
        community=get_community(request)
        cache_key=f'datasets_{community.name}'
        datasets = cache.get(cache_key)
        if datasets:
            return datasets
        try:
            tli = TwitterLanguageIdentifier.objects.get(tag=community.language)
        except TwitterLanguageIdentifier.DoesNotExist:
            tli=None
        datasets = []
        user_id = get_user_id(request)
        if user_id:
            data_user = CreationFollowerChartData.get_data([user_id])
        member_userid_lst = get_userid_lst(request,lang=tli)
        if settings.DEBUG:
            member_userid_lst=member_userid_lst[:]
        try:
            member_userid_lst.remove(user_id)
        except ValueError:
            pass
        bot_id = get_bot_id(request)
        if bot_id:
            data_bot = CreationFollowerChartData.get_data([bot_id])
            dataset_bot = {
                'label': _('Bot'),
                'backgroundColor': rgb_to_rgba("blue", alpha=0.5),
                'borderColor': 'blue',
                'data': data_bot,
                'pointRadius': 7
            }
            datasets.append(dataset_bot)
        data_all = CreationFollowerChartData.get_data(member_userid_lst)
        dataset_all = {
            'label': _('All followers'),
            'backgroundColor': rgb_to_rgba("grey", alpha=0.5),
            'borderColor': 'grey',# webcolors.name_to_rgb('grey'),
            'data': data_all,
        }
        datasets.append(dataset_all)
        dataset_user = {
            'label': _('You'),
            'backgroundColor': rgb_to_rgba("red", alpha=0.5),
            'borderColor': 'red',
            'data': data_user,
            'pointRadius': 7
        }
        datasets.append(dataset_user)
        cats: [dict] = [
            {"cat_obj":ccr.category, "cat_color":ccr.color} for ccr
            in CommunityCategoryRelationship.objects.filter(
                community=community,
                follower_chart=True,
            )
        ]
        logger.debug(f'{cats=}')
        for cat in cats:
            label = cat["cat_obj"].label
            color = cat["cat_color"]
            category=cat["cat_obj"]
            logger.debug(f'{category=}')
            data = CreationFollowerChartData.get_data(
                member_userid_lst,
                category=category
            )
            cat_data_set = {
                'label': label,
                'backgroundColor': color,
                'borderColor': color,
                'data': data,
                'hidden':  (
                    False if (category in community.membership.all())
                    else True
                )
            }
            datasets.append(cat_data_set)
        cache.set(cache_key,datasets,TTL)
        return datasets

    @staticmethod
    def get_data(userid_lst, category=None):
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
                dct = data.pop(i)
            except IndexError:
                continue
            twitter_datetime: str =  dct.pop("profile__json__created_at")
            if not twitter_datetime:
                continue
            python_datetime = get_datetime_tz_from_twitter_str(twitter_datetime)
            dct["x"] = python_datetime.date().isoformat()
            user_id = dct.pop("profile__json__id")
            dct["y"] = CreationFollowerChartData.follower_count(
                user_id,
                category=category,
            )
            dct["id"] = user_id
            dct["screen_name"] = dct.pop("profile__json__screen_name")
            data.insert(i, dct)
        return data

    def get(self, request, format=None):
        datasets = CreationFollowerChartData.datasets(request)
        """
        res = {
            "data_all": None,
            "data_bot": None,
            "data_user": None,
        }

        user_id = get_user_id(request)
        if user_id:
            data = CreationFollowerChartData.get_data([user_id])
            res["data_user"] = data

        member_userid_lst = get_userid_lst(request)
        try:
            member_userid_lst.remove(user_id)
        except ValueError:
            pass
        data_all = CreationFollowerChartData.get_data(member_userid_lst)
        res["data_all"] = data_all

        bot_id = get_bot_id(request)
        if bot_id:
            data = CreationFollowerChartData.get_data([bot_id])
            res["data_bot"] = data
        """

        for dct in datasets:
            logger.debug(
                f'{type(dct)=}\n{len(dct)}\n{dct["data"][:10]}\n\n'
            )
        res = {
            "title": _(
                "Follower count (total and by category) vs. creation date of "
                "the account."
            ),
            "datasets": datasets
        }
        logger.debug(f'{type(res)=}')
        logger.debug(f'{len(res)=}')
        return Response(res)