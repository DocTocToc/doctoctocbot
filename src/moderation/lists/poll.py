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

from bot.twitter import getAuth, get_api
from moderation.models import SocialUser, SocialMedia, Category, UserCategoryRelationship

from .constants import MODERATOR, CATEGORIES_DICT as CAT

#os.environ["DJANGO_SETTINGS_MODULE"] = 'doctocnet.settings'
#django.setup()

logging.basicConfig(level=logging.DEBUG)

noi = -1 # number of items

# get or create SocialUser corresponding to the bot (belonging to moderator category)
def get_or_create_category(cat):
    cat_subdict = CAT.get(cat)
    label_en = cat_subdict.get("label_en")
    label_fr = cat_subdict.get("label_fr")
    cat_mi, _ = Category.objects.get_or_create(name = cat, label_en = label_en, label_fr = label_fr)
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
    if category not in user.category.all():
        user_category_relationship = UserCategoryRelationship(
            social_user = user,
            category = category,
            moderator = moderator_mi
        )
        user_category_relationship.save()
        
def remove_usercategoryrelationship(user_mis, category):
    for user_mi in user_mis:
        if category in user_mi.category.all():
            ucr = UserCategoryRelationship.objects.filter(social_user = user_mi,
                                                      category = category)
            ucr.delete()

def poll():
    debug = settings.DEBUG
    bot_id = settings.BOT_ID
    bot_screen_name = settings.BOT_SCREEN_NAME
    
    # create Tweepy api object
    auth = getAuth()
    api = tweepy.API(auth, wait_on_rate_limit=True)
    
    lists = api.lists_all(bot_screen_name, bot_id)
    
    # create some defaults
    socmedtwitter_mi, _ = SocialMedia.objects.get_or_create(name='twitter')
    bot_socialuser_mi = get_or_create_social_user(bot_id, socmedtwitter_mi)
    moderator_category_mi = get_or_create_category(MODERATOR)
    check_add_usercategoryrelationship(bot_socialuser_mi, moderator_category_mi, bot_socialuser_mi)

    for l in lists:
        for k, v in CAT.items():
            # Test account: use list slug to find category
            if debug:
                logging.debug(f'l.slug: {l.slug}, v["slug"]: {v["slug"]}')
                if l.slug == v["slug"]:
                    category = k
                
            else:
                # Production account: use list id to find category
                logging.debug(f'l.id: {l.id}, v["id"]: {v["id"]}')
                if l.id == v["id"]:
                    category = k

        try:
            category
        except NameError:
            logging.error(f"The list {l.slug} does not correspond to any known category of users.")
            continue
            
        # check for new user in the list and add to corresponding category
        category_mi = get_or_create_category(category)
        
        users_id = []
        for member in tweepy.Cursor(api.list_members, bot_screen_name, l.slug).items(noi):
            socialuser_mi = get_or_create_social_user(user_id = member.id, socialmedia_mi = socmedtwitter_mi)
            check_add_usercategoryrelationship(socialuser_mi, category_mi, bot_socialuser_mi)
            users_id.append(member.id)
        
        # remove users that are not in the list users_id from category
        socialusers_mis = SocialUser.objects.filter(category__name=category)
        logging.debug(f'socialusers_mi: {socialusers_mis}')
        socialusers_mis_twitter = SocialUser.objects.filter(category__name=category).filter(user_id__in=users_id)
        to_delete_mis = socialusers_mis.difference(socialusers_mis_twitter)
        logging.debug(f"to_delete_mis: {to_delete_mis}")
        remove_usercategoryrelationship(to_delete_mis, category_mi)

def backup_lists():
    bot_id = settings.BOT_ID
    bot_screen_name = settings.BOT_SCREEN_NAME
    api = get_api()
    lists = api.lists_all(bot_screen_name, bot_id)
    if not lists:
        return
    dir = settings.LISTS_BACKUP_PATH
    if not os.path.isdir(dir):
        return
    datetime_str = datetime.now().isoformat(timespec='seconds')
    date_str = datetime.now().date().isoformat()
    dir_date = dir + "/" + date_str
    os.makedirs(dir_date, exist_ok=True)
    for list in lists:
        file = (dir_date
                + "/"
                + list.slug
                + "_"
                + str(list.member_count)
                + "_"
                + datetime_str)
        cursor = tweepy.Cursor(api.list_members, bot_screen_name, list.slug).items(noi)
        id_lst = [member.id for member in cursor]
        with open(file, 'xb') as f:
            pickle.dump(id_lst, f)
            
if __name__ == "__main__":
    # create bot
    auth = getAuth()
    api = tweepy.API(auth, wait_on_rate_limit=True)
    poll()