import logging
from random import sample
from typing import Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List
from django.utils import timezone
from bot.tweepy_api import get_api
from django.db.utils import DatabaseError
from django.db import IntegrityError
from moderation.social import update_social_ids
from django.conf import settings
from community.models import Community
from moderation.models import (
    SocialUser,
    Friend,
    Follower,
    SocialMedia,
    Profile,
    Prospect,
    UserCategoryRelationship,
    Category,
)
from tweepy.error import TweepError

logger = logging.getLogger(__name__)

@dataclass
class User:
    id: int
    latest: datetime = None

    def __repr__(self):
        if self.latest:
            dt=datetime.strftime(self.latest, '%Y/%m/%d %H:%M:%S')
        else:
            dt=""
        return(
            f"User:\n"
            f"    id: {self.id}\n"
            f"    latest: {dt}\n"
        )


@dataclass
class Candidates:
    users: List[User]

    def __repr__(self):
        return "Users:\n{}".format('\n'.join(self.users))


class Follow():
    def __init__(
            self,
            socialuser: SocialUser,
            count: Optional[int] = None,
            delta: Optional[int] = 7, # days
            force_follow: bool = False,
            sample: Optional[int] = None,
        ):
        self.socialuser = socialuser
        self.friends: List[int] = self.get_friends()
        self.community = self.get_community()
        self.network: List[Community] = self.get_network()
        self.count = count
        self.api = self.get_api()
        self.candidates: List[User] = []
        self.delta = delta
        self.force_follow = force_follow
        self.sample = sample

    def process(self):
        if self.count is None:
            return
        self.candidates = []
        logger.debug(f'0. Count:{len(self.candidates)}\n{self.candidates}')
        self.update_social()
        self.add_potential_members()
        logger.debug(f'\n1. Count:{len(self.candidates)}\n{self.candidates}')
        self.add_prospects()
        logger.debug(f'\n2. Count:{len(self.candidates)}\n{self.candidates}')
        if self.sample:
            self.candidates[:]=self.random_sample(self.candidates)
        logger.debug(f'\n3. Count:{len(self.candidates)}\n{self.candidates}')
        self.friend_latest()
        logger.debug(f'\n4. Count:{len(self.candidates)}\n{self.candidates}')
        if self.delta:
            self.filter_latest()
        logger.debug(f'\n5. Count:{len(self.candidates)}\n{self.candidates}')
        self.order_latest()
        logger.debug(f'\n6. Count:{len(self.candidates)}\n{self.candidates}')
        self.filter_count()
        logger.debug(f'\n7. Count:{len(self.candidates)}\n{self.candidates}')
        followed_dict = self.follow()
        logger.info(followed_dict)

    def get_api(self):
        return get_api(
            username=self.socialuser.screen_name_tag(),
            backend=True
        )

    def get_community(self):
        try:
            return self.socialuser.account.community
        except:
            return

    def get_network(self):
        community_list = [self.community]
        for network in self.community.network_set.all():
            for community in network.community.all():
                community_list.append(community)
        return community_list

    def get_friends(self):
        try:
            return Friend.objects.filter(user=self.socialuser).latest("id").id_list
        except Friend.DoesNotExist:
            logger.error(
                f'No Friend object for SocialUser {self.socialuser} was found'
            )
            return []

    def random_sample(self, iterable):
        if self.sample > len(iterable) or self.sample < 0:
            return iterable
        return sample(
            iterable,
            self.sample
        )

    def order_latest(self):
        candidates = [user for user in self.candidates if not user.latest]
        candidates.extend(
            sorted(
                [user for user in self.candidates if user.latest],
                key=lambda t: datetime.strftime(t.latest, '%Y/%m/%d %H:%M:%S')
            )
        )
        self.candidates=candidates

    def filter_count(self):
        del self.candidates[self.count:]

    def follow(self):
        if settings.DEBUG and not self.force_follow:
            for user in self.candidates:
                logger.debug(f"{user} was followed.")
        else:
            followed_dict = {
                "candidates": len(self.candidates),
                "followed": 0    
            }
            for idx, user in enumerate(self.candidates):
                try:
                    response = self.api.create_friendship(user_id=str(user.id))
                except TweepError as e:
                    logger.error(e)
                    followed_dict.update({
                        idx: {'error': str(e)}
                    })
                    continue
                try:
                    screen_name = response._json['screen_name']
                    logger.debug(
                        f"User {screen_name} was followed\n ({user})"
                    )
                    followed_dict.update({
                        idx: {'screen_name': screen_name},
                        'followed': followed_dict['followed'] + 1
                    })
                except:
                    logger.error(response)
                    followed_dict.update({
                        idx: {'error': str(response)}
                    })
                    continue
            return followed_dict

    def update_social(self):
        for relationship in ['friends', 'followers']:
            update_social_ids(
                user=self.socialuser,
                bot_screen_name=self.socialuser.screen_name_tag(),
                relationship=relationship    
            )      

    def create_update_profiles(self):
        n = 100
        ids = [user.id for user in self.candidates]
        # do not update recently updated profiles
        one_day_ago = timezone.now() - timedelta(days=1) 
        ids_recent_update = (
            SocialUser.objects
            .filter(profile__updated__gte=one_day_ago)
            .values_list("user_id", flat=True)
        )
        ids[:] = [ id_ for id_ in ids if id_ not in ids_recent_update]
        split: List[List[int]] = [ids[i:i+n] for i in range(0, len(ids), n)]
        try:
            twitter = SocialMedia.objects.get(name='twitter')
        except SocialMedia.DoesNotExist:
            return
        for ids in split:
            try:
                users = self.api.lookup_users(ids)
            except TweepError as e:
                logger.error(e)
                continue
            for user in users:
                try:
                    su, _ = SocialUser.objects.get_or_create(
                        user_id = user.id,
                        social_media = twitter
                    )
                except DatabaseError:
                    continue
                if hasattr(su, 'profile'):
                    su.profile.json = user._json
                    su.profile.save()
                else:
                    try:
                        Profile.objects.create(socialuser=su, json=user._json)
                    except IntegrityError as e:
                        logger.debug(e)
                        continue

    def add_potential_members(self):
        potential_members_ids = list(
            UserCategoryRelationship.objects
            .filter(community__in=self.network)
            .filter(category__in=self.community.membership.all())
            .exclude(
                social_user__in=SocialUser.objects.filter(
                    user_id__in=self.friends
                    )
                )
            .exclude(
                category__in=Category.objects.filter(
                    community_relationship__do_not_follow=True,
                    community_relationship__community=self.community,
                )
            ).values_list("social_user__user_id", flat=True)
        )
        logger.debug(f'{potential_members_ids=}')
        if self.sample and potential_members_ids:
            potential_members_ids[:] = self.random_sample(
                potential_members_ids
            )
        for user_id in potential_members_ids:
            self.candidates.append(User(user_id))

    def add_prospects(self):
        prospects_ids = list(
            Prospect.objects.filter(
                community=self.community,
                active=True,
            ).exclude(
                socialuser__user_id__in=self.friends
            ).values_list("socialuser__user_id", flat=True)
        )
        logger.debug(f'{prospects_ids=}')
        if self.sample and prospects_ids:
            prospects_ids[:] = self.random_sample(
                prospects_ids
            )
        for user_id in prospects_ids:
            self.candidates.append(User(user_id))

    def filter_latest(self):
        self.candidates[:] = [
            user for user in self.candidates if self.process_delta(user)
        ]

    def process_delta(self, user):
        if not user.latest:
            return True
        delta_computed: timedelta = timezone.now() - user.latest
        delta_limit = timedelta(days=self.delta)
        return delta_computed > delta_limit

    def friend_latest(self):
        for user in self.candidates:
            try:
                latest_friend = Friend.objects \
                .filter(user=self.socialuser) \
                .filter(id_list__contains=[user.id]) \
                .latest("id")
            except Friend.DoesNotExist:
                continue
            user.latest = latest_friend.created