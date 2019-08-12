#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Poll Twitter lists of bot account and populate usercategoryrelationship table

This module allows for a smooth transition from solo moderation through the
Twitter account to group moderation.
"""

#import django
import logging
import os
import tweepy
#import inspect
from datetime import datetime
import pickle

from django.conf import settings

from django.db.utils import DatabaseError

from bot.twitter import get_api
from moderation.models import SocialUser, SocialMedia, Category, UserCategoryRelationship

from .constants import MODERATOR
from moderation.models import TwitterList
from bot.lib.datetime import datetime_twitter_str

#os.environ["DJANGO_SETTINGS_MODULE"] = 'doctocnet.settings'
#django.setup()

logger = logging.getLogger(__name__)

noi = -1 # number of items

# get or create SocialUser corresponding to the bot (belonging to moderator category)
def get_or_create_category(cat):
    try:
        twitter_list_mi = TwitterList.objects.get(uid=cat)
    except TwitterList.DoesNotExist:
        logger.error("Category %s does not exist in TwitterList table." % cat)
        return

    label = twitter_list_mi.label
    try:
        cat_mi = Category.objects.get(name=cat)
    except Category.DoesNotExist:
        cat_mi = Category.objects.create(name=cat, label=label)

    return cat_mi
    
def get_or_create_social_user(user_id, socialmedia_mi):
    try:
        socialuser = SocialUser.objects.get(user_id = user_id)
    except SocialUser.DoesNotExist:
        socialuser = SocialUser(
            user_id = user_id,
            social_media = socialmedia_mi
        )
        socialuser.save()
    return socialuser

def check_add_usercategoryrelationship(user, category, moderator_mi):
    if not user or not category or not moderator_mi:
        return
    if category not in user.category.all():
        user_category_relationship = UserCategoryRelationship(
            social_user = user,
            category = category,
            moderator = moderator_mi
        )
        try:
            user_category_relationship.save()
        except DatabaseError as e:
            logger.error("Database error while trying to add a new "
                         "UserCategoryRelationship instance: %r", e)
        
def remove_usercategoryrelationship(user_mis, category):
    for user_mi in user_mis:
        if category in user_mi.category.all():
            ucr = UserCategoryRelationship.objects.filter(social_user = user_mi,
                                                      category = category)
            ucr.delete()

def get_twitter_lists():
    bot_id = settings.BOT_ID
    bot_screen_name = settings.BOT_SCREEN_NAME
    api = get_api()
    return api.lists_all(bot_screen_name, bot_id)

def poll_lists_members():
    # create some defaults if they don't exist
    socmedtwitter_mi, _ = SocialMedia.objects.get_or_create(name='twitter')
    bot_socialuser_mi = get_or_create_social_user(settings.BOT_ID, socmedtwitter_mi)
    moderator_category_mi = get_or_create_category(MODERATOR)
    check_add_usercategoryrelationship(bot_socialuser_mi, moderator_category_mi, bot_socialuser_mi)
    
    lists = get_twitter_lists()
    
    for list in lists:
        try:
            twitter_list_mi = TwitterList.objects.get(list_id=list.id)
        except TwitterList.DoesNotExist:
            logger.error("List %i does not exist in TwitterList table." % list.id)
            continue
        category_name = twitter_list_mi.uid
        category_mi = get_or_create_category(category_name)
        users_id = []
        for member in tweepy.Cursor(
            get_api().list_members,
            settings.BOT_SCREEN_NAME,
            twitter_list_mi.slug).items(noi):
            socialuser_mi = get_or_create_social_user(user_id = member.id, socialmedia_mi = socmedtwitter_mi)
            check_add_usercategoryrelationship(socialuser_mi, category_mi, bot_socialuser_mi)
            users_id.append(member.id)
        
        # remove users that are not in the list users_id from category
        #socialusers_mis = SocialUser.objects.filter(category__name=category_name)
        #logging.debug(f'socialusers_mi: {socialusers_mis}')
        #socialusers_mis_twitter = SocialUser.objects.filter(category__name=category_name).filter(user_id__in=users_id)
        #to_delete_mis = socialusers_mis.difference(socialusers_mis_twitter)
        #logging.debug(f"to_delete_mis: {to_delete_mis}")
        #remove_usercategoryrelationship(to_delete_mis, category_mi)

        # TODO: remove from twitter list users that are not in the category

def create_update_lists():
    lists = get_twitter_lists()
    for list in lists:
        create_update_list(list)

def create_update_list(list):
    if TwitterList.objects.filter(list_id=list.id).exists():
        update_twitter_list(list)
    else:
        create_twitter_list(list)
        
def update_twitter_list(list):
    try:
        twitter_list_mi = TwitterList.objects.get(list_id=list.id)
    except TwitterList.DoesNotExist:
        return
    
    twitter_list_mi.slug=list.slug
    twitter_list_mi.name=list.name
    twitter_list_mi.twitter_description=list.description
    twitter_list_mi.json=tweepy_list_json(list)
    try:
        twitter_list_mi.save(update_fields=['slug', 'name', 'twitter_description', 'json'])
    except DatabaseError:
        logger.error("Error during TwitterList %s instance update." % list.id) 

def create_twitter_list(list):
    try:
        TwitterList.objects.create(
            list_id=list.id,
            slug=list.slug,
            name=list.name,
            uid=list.slug,
            label=list.name,
            twitter_description=list.description,
            local_description=list.description,
            json=tweepy_list_json(list)
        )
    except DatabaseError:
        logger.error("Error during TwitterList creation.")
    
def tweepy_list_json(list):
    lst_dict = {}
    lst_dict["id"] = list.id
    lst_dict["slug"] = list.slug
    lst_dict["name"] = list.name
    lst_dict["created_at"] = datetime_twitter_str(list.created_at)
    lst_dict["uri"] = list.uri
    lst_dict["subscriber_count"] = list.subscriber_count
    lst_dict["id_str"] = list.id_str
    lst_dict["member_count"] = list.member_count
    lst_dict["mode"] = list.mode
    lst_dict["full_name"] = list.full_name
    lst_dict["description"] = list.description
    lst_dict["user"] = list.user._json
    return lst_dict
