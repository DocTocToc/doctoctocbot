import logging
import pytz
import time
import itertools
from datetime import timedelta, datetime
from typing import List, Optional
from collections import Counter
from moderation.models import (
    Friend,
    Follower,
    SocialUser,
    Category,
    UserCategoryRelationship
)
from community.models import Community
from conversation.models import Tweetdj
from moderation.social import update_social_ids
from community.helpers import get_community_bot_socialuser
from moderation.profile import create_twitter_social_user_and_profile

logger = logging.getLogger(__name__)

class Prospect():
    def __init__(
            self,
            community: Community,
            category: Category,
            min_follower: Optional[int] = None,
            min_friend: Optional[int] = None,
            network_cache: Optional[int] = None,
            most_common:  Optional[int] = None
        ):
        self.community=community
        self.category=category
        self.bot=get_community_bot_socialuser(self.community)
        self.candidates: List[SocialUser] = []
        self.network: List[Community] = self.get_network()
        self.members_user_id: List[int] = self.get_members_user_id()
        self.members_su_id: List[int] = self.get_members_su_id()
        self.friends: Optional[Counter] = None
        self.followers: Optional[Counter] = None
        self.min_follower=min_follower or 5
        self.min_friend=min_friend or 5
        self.network_cache = network_cache or 7
        self.most_common = most_common

    def graph_count(self, socialuser, relationship):
        if relationship == 'follower':
            Model = globals()['Follower']
            relationship_key = "followers_count"
        elif relationship == 'friend':
            Model = globals()['Friend']
            relationship_key = "friends_count"
        else:
            return
        try:
            return len(
                Model.objects.filter(user=socialuser).latest('id').id_list
            )
        except Model.DoesNotExist:
            try:
                return socialuser.profile.json[relationship_key]
            except:
                try:
                    return Tweetdj.objects \
                            .filter(socialuser=socialuser) \
                            .latest('statusid') \
                            .json["user"][relationship_key]
                except:
                    return

    def get_network(self):
        community_list = [self.community]
        for network in self.community.network_set.all():
            for community in network.community.all():
                community_list.append(community)
        return community_list

    def get_members_qs(self):
        return (
            UserCategoryRelationship.objects
            .filter(community__in=self.network)
            .filter(category=self.category)
            .exclude(
                category__in=Category.objects.filter(
                    community_relationship__do_not_follow=True,
                    community_relationship__community=self.community,
                )
            )
        )

    def get_members_user_id(self):
        qs = self.get_members_qs()
        return list(
            qs.values_list("social_user__user_id", flat=True)
        )

    def get_members_su_id(self):
        qs = self.get_members_qs()
        return list(
            qs.values_list("social_user__id", flat=True)
        )

    def known_network(self):
        cache_delta=timedelta(days=self.network_cache)
        datetime_limit = datetime.now(pytz.utc) - cache_delta
        cached_friends=Friend.objects.filter(
            user__id__in=self.members_su_id,
            created__gte=datetime_limit
        ).values('id').count()
        cached_friends_ratio =  cached_friends / len(self.members_su_id)
        cached_followers=Follower.objects.filter(
            user__id__in=self.members_su_id,
            created__gte=datetime_limit
        ).values('id').count()
        cached_followers_ratio =  cached_followers / len(self.members_su_id)
        return f'{cached_friends_ratio=}\n{cached_followers_ratio=}\n'

    def update_network(self):
        for su_id in self.members_su_id:
            try:
                su=SocialUser.objects.get(id=su_id)
            except SocialUser.DoesNotExist:
                continue
            logger.info(f'{self.known_network()}')
            for relationship in ['friends', 'followers']:
                update_social_ids(
                    su,
                    cached=True,
                    bot_screen_name=self.bot.screen_name_tag(),
                    relationship=relationship,
                    delta=timedelta(days=self.network_cache),
                )

    def update_bot_network(self):
        for relationship in ['friends', 'followers']:
            update_social_ids(
                self.bot,
                cached=False,
                bot_screen_name=self.bot.screen_name_tag(),
                relationship=relationship
            )

    def get_friends(self):
        lst = []
        for su_id in self.members_su_id:
            try:
                lst.extend(
                    Friend.objects.filter(user__id=su_id).latest('id').id_list
                )
            except Friend.DoesNotExist:
                continue
        return Counter(lst)

    def get_followers(self):
        lst = []
        for su_id in self.members_su_id:
            try:
                lst.extend(
                    Follower.objects.filter(user__id=su_id).latest('id').id_list
                )
            except Follower.DoesNotExist:
                continue
        return Counter(lst)
    
    def subtract_members(self):
        members = Counter(self.members_user_id)
        self.friends.subtract(members)
        self.followers.subtract(members)

    def add_social_users(self, friends: int, followers: int):
        all_set = set(self.followers.elements()) | set(self.friends.elements())
        for user_id in all_set:
            if (
                self.friends[user_id] >= friends
                and self.followers[user_id] >= followers
            ):
                create_twitter_social_user_and_profile(
                    user_id,
                    cache=True
                )

    def display(self):
        #logger.debug(f'{self.friends.total()=}')
        #logger.debug(f'{self.followers.total()=}')
        m_c_follower = self.most_common or self.min_follower
        m_c_friend = self.most_common or self.min_friend
        friends_m_c = self.friends.most_common(m_c_friend)
        followers_m_c = self.followers.most_common(m_c_follower)
        uid_set = set()
        for lst_tpl in [friends_m_c, followers_m_c]:
            lst = [tpl[0] for tpl in lst_tpl]
            #logger.debug(lst)
            uid_set |= set(lst)
        su_lst = list(SocialUser.objects.filter(user_id__in=uid_set))
        su_lst[:] = [
            su for su in su_lst
            if self.friends[su.user_id] >= self.min_friend
            and self.followers[su.user_id] >= self.min_follower
            and (
                self.graph_count(su, 'follower')
                and
                (self.friends[su.user_id]/self.graph_count(su,'follower')>0.01)
            )
        ]
        su_lst_friend=sorted(
            su_lst,
            key=lambda su: self.friends[su.user_id],
            reverse=True
        )
        su_lst_follower=sorted(
            su_lst,
            key=lambda su: self.followers[su.user_id],
            reverse=True
        )
        
        display_str = self.known_network()
        display_str += (
            f'\n{m_c_friend=} Friends '
            f'(among {self.friends.total()}):'
            '\n'
        )
        
        friend_str = ""
        str_len = len(str(len(su_lst_friend)))
        for count, su in enumerate(su_lst_friend):
            friend_str += (
                f'{str(count).zfill(str_len)}. '
                f'count:{self.friends[su.user_id]} '
                f'{su.user_id} '
                f'{su.screen_name_tag()}'
                '\n'
            )
        display_str += friend_str
        display_str += (
            f'\n{m_c_follower=} Followers '
            f'(among {self.followers.total()}):'
            '\n'
        )
        follower_str = ""
        str_len = len(str(len(su_lst_follower)))
        for count, su in enumerate(su_lst_follower):
            follower_str += (
                f'{str(count).zfill(str_len)}. '
                f'count:{self.followers[su.user_id]} '
                f'{su.user_id} '
                f'{su.screen_name_tag()}'
                '\n'
            )
        display_str += follower_str
        return display_str