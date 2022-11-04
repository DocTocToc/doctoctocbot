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
        twitteruserid_list = get_userid_lst(self.request,lang=tli)
        if settings.DEBUG:
            twitteruserid_list=twitteruserid_list[:]
        return twitteruserid_list

    def follower_count(self, user_id, category=None):
        if settings.DEBUG:
            TTL=600
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
        cache.set(
            f'follower_count_{user_id}_{category.name}',
            count,
            TTL
        )
        return count

    def get_dataset(self, category=None, label=None, color=None):
        if settings.DEBUG:
            TTL=600
        else:
            TTL=config.creation_follower_datasets_ttl
        if category:
            cache_key=f'dataset_{self.community.name}_{category.name}'
        else:
            cache_key=f'dataset_{self.community.name}_all'
        dataset = cache.get(cache_key)
        if dataset:
            return dataset
        if category:
            label=label
            hidden = (
                False if (category in self.community.membership.all())
                else True
            )
            backgroundColor=rgb_to_rgba(color, alpha=0.4)
            borderColor= color
        else:
            label=_('All followers')
            hidden=True
            backgroundColor= rgb_to_rgba("grey", alpha=0.2)
            borderColor='grey'
        dataset = {
            'label': label,
            'backgroundColor': backgroundColor,
            'borderColor': borderColor,
            'data': self.get_data(category=category),
            'hidden': hidden,
            'pointRadius': None,
            'pointStyle': None,
        }
        cache.set(cache_key,dataset,TTL)
        return dataset

    def datasets(self):
        if settings.DEBUG:
            TTL=60
        else:
            TTL=config.creation_follower_datasets_ttl
        cache_key=f'datasets_{self.community.name}_{self.twitteruserid}'
        datasets = cache.get(cache_key)
        if datasets:
            return datasets
        datasets = []
        dataset_all = self.get_dataset()
        if not (self.twitteruserid in self.twitteruserid_list):
            user_data_point=self.get_data(tuid=self.twitteruserid)
            dataset_all["data"].extend(user_data_point)
        if not (self.bot_twitteruserid in self.twitteruserid_list):
            bot_data_point=self.get_data(tuid=self.bot_twitteruserid)
            dataset_all["data"].extend(bot_data_point)
        logger.debug(f'{dataset_all["data"]} {type(dataset_all["data"])}')
        dataset_all["data"].sort(key=lambda x: x["id"])
        dataset_all['pointRadius']=self.get_pointRadius()
        dataset_all['pointStyle']=self.get_pointStyle()
        datasets.append(dataset_all)
        for cat in self.cats:
            label = cat["cat_obj"].label
            color = cat["cat_color"]
            category=cat["cat_obj"]
            dataset = self.get_dataset(
                category=category,
                label=label,
                color=color
            )
            if not (self.twitteruserid in self.twitteruserid_list):
                user_data_point=self.get_data(
                    tuid=self.twitteruserid,
                    category=category
                )
                dataset["data"].extend(user_data_point)
            if not (self.bot_twitteruserid in self.twitteruserid_list):
                bot_data_point=self.get_data(
                    tuid=self.bot_twitteruserid,
                    category=category
                )
                dataset["data"].extend(bot_data_point)
            dataset["data"].sort(key=lambda x: x["id"])
            dataset['pointRadius']=self.get_pointRadius()
            dataset['pointStyle']=self.get_pointStyle()
            datasets.append(dataset)
        cache.set(cache_key,datasets,TTL)
        return datasets

    def get_pointStyle(self)->[str]:
        _list = self.tuid_list_user_bot()
        lst=["circle"]*len(_list)
        if self.bot_twitteruserid:
            try:
                bot_idx=_list.index(self.bot_twitteruserid)
                lst.pop(bot_idx)
                lst.insert(bot_idx, "triangle")
            except ValueError:
                pass
        if self.twitteruserid:
            try:
                user_idx=_list.index(self.twitteruserid)
                lst.pop(user_idx)
                lst.insert(user_idx, "rect")
            except ValueError:
                pass
        return lst

    def tuid_list_user_bot(self):
        _list = self.twitteruserid_list
        if (self.bot_twitteruserid and not (self.bot_twitteruserid in _list)):
            _list.append(self.bot_twitteruserid)
        if (self.twitteruserid and not (self.twitteruserid in _list)):
            _list.append(self.twitteruserid)
        _list.sort()
        return _list

    def get_pointRadius(self)->[int]:
        def_rad=config.creation_follower_default_radius
        bot_rad=config.creation_follower_bot_radius
        user_rad=config.creation_follower_user_radius
        _list = self.tuid_list_user_bot()
        lst=[def_rad]*len(_list)
        if self.bot_twitteruserid:
            try:
                bot_idx=_list.index(self.bot_twitteruserid)
                lst.pop(bot_idx)
                lst.insert(bot_idx, bot_rad)
            except ValueError:
                pass
        if self.twitteruserid:
            try:
                user_idx=_list.index(self.twitteruserid)
                lst.pop(user_idx)
                lst.insert(user_idx, user_rad)
            except ValueError:
                pass
        return lst

    def get_data(self, tuid=None, category=None):
        if tuid:
            tuid_list=[tuid]
        else:
            tuid_list=self.twitteruserid_list
        try:
            socmed = SocialMedia.objects.get(name="twitter")
        except SocialMedia.DoesNotExist:
            return
        data = list(
            SocialUser.objects
            .filter(
                user_id__in=tuid_list,
                social_media=socmed,
            )
            .values(
                "profile__json__created_at",
                "profile__json__followers_count",
                "profile__json__screen_name",
                "profile__json__id",)

        )
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
                    "You must be authenticated to see this chart."
                ),
                "datasets": []
            }
            return Response(res)
        self.request=request
        self.community=get_community(request)
        self.cats: [dict] = [
            {"cat_obj":ccr.category, "cat_color":ccr.color} for ccr
            in CommunityCategoryRelationship.objects.filter(
                community=self.community,
                follower_chart=True,
            )
        ]
        self.twitteruserid = get_twitter_user_id(request)
        self.bot_twitteruserid = get_bot_id(request)
        self.twitteruserid_list=self.get_twitteruserid_list()
        self.twitteruserid_list.sort()
        datasets = self.datasets()
        try:
            bot_username = SocialUser.objects.get(
                user_id=self.bot_twitteruserid
            ).screen_name_tag()
        except:
            bot_username = _("the bot")
        categories = (
            ", ".join([cat["cat_obj"].label for cat in self.cats])
        )
        or_string = _("or") + " "
        members = or_string.join(
            [cat.label for cat in self.community.membership.all()]
        )
        res = {
            "title": _(
                "Follower count (total and by category) vs. creation date of "
                "the account. ■ is you, ▲ is {bot}."
            ).format(bot=f'@{bot_username}'),
            "subtitle": _(
                "Click on categories (All followers, {categories}) to display "
                "or hide data. tldr; if the triangle is higher than the square"
                " for the category {members}, you should follow {bot}"
                ).format(
                    categories=categories,
                    members=members,
                    bot=f'@{bot_username}'
                ),
            "datasets": datasets
        }
        return Response(res)