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
from moderation.models import (
    SocialUser,
    Friend,
    Follower,
    SocialMedia,
    Profile,
    Prospect,
)
from tweepy.error import TweepError

logger = logging.getLogger(__name__)

@dataclass
class User:
    id: int
    since: datetime = None

    def __repr__(self):
        if self.since:
            dt=datetime.strftime(self.since, '%Y/%m/%d %H:%M:%S')
        else:
            dt=""
        return(
            f"User:\n"
            f"    id: {self.id}\n"
            f"    since: {dt}\n"
        )


@dataclass
class Candidates:
    users: List[User]

    def __repr__(self):
        return "Users:\n{}".format('\n'.join(self.users))


class Unfollow():
    def __init__(
            self,
            socialuser: SocialUser,
            transfer: bool = False,
            to_socialuser: Optional[SocialUser] = None,
            count: Optional[int] = None,
            delta: Optional[int] = 7, # days
            force_unfollow: bool = False,
            sample: Optional[int] = None,
        ):
        self.socialuser = socialuser
        self.transfer = transfer
        self.to_socialuser = to_socialuser,
        self.count = count
        self.api = self.get_api()
        self.candidates: List[User] = []
        self.delta = delta
        self.force_unfollow = force_unfollow
        self.sample = sample

    def process(self):
        if self.count is None:
            return
        self.candidates = []
        logger.debug(f'0. Count:{len(self.candidates)}\n{self.candidates}')
        self.update_social()
        self.get_no_follow_back()
        if self.sample:
            self.random_sample()
        self.add_prospect()
        logger.debug(f'\n1. Count:{len(self.candidates)}\n{self.candidates}')
        self.friend_since()
        if self.delta:
            self.filter_since()
        logger.debug(f'\n2. Count:{len(self.candidates)}\n{self.candidates}')
        self.filter_protected()
        logger.debug(f'\n3. Count:{len(self.candidates)}\n{self.candidates}')
        self.order_since()
        logger.debug(f'\n4. Count:{len(self.candidates)}\n{self.candidates}')
        self.filter_count()
        logger.debug(f'\n5. Count:{len(self.candidates)}\n{self.candidates}')
        unfollowed_dict = self.unfollow()
        logger.info(unfollowed_dict)

    def get_api(self):
        return get_api(
            username=self.socialuser.screen_name_tag(),
            backend=True
        )

    def random_sample(self):
        self.candidates[:] = sample(
            self.candidates,
            self.sample
        )

    def order_since(self):
        self.candidates[:] = sorted(
            self.candidates,
            key=lambda t: datetime.strftime(t.since, '%Y/%m/%d %H:%M:%S'),
        )

    def filter_count(self):
        del self.candidates[self.count:]

    def unfollow(self):
        if settings.DEBUG and not self.force_unfollow:
            for user in self.candidates:
                logger.debug(f"{user} was unfollowed.")
        else:
            unfollowed_dict = {
                "candidates": len(self.candidates),
                "unfollowed": 0    
            }
            for idx, user in enumerate(self.candidates):
                response = self.api.destroy_friendship(user_id=str(user.id))
                try:
                    screen_name = response._json['screen_name']
                    logger.debug(
                        f"User {screen_name} was unfollowed\n ({user})"
                    )
                    unfollowed_dict.update({
                        idx: {'screen_name': screen_name},
                        'unfollowed': unfollowed_dict['unfollowed'] + 1
                    })
                except:
                    logger.error(response)
                    unfollowed_dict.update({
                        idx: {'error': str(response)}
                    })
                    continue
            return unfollowed_dict

    def add_prospect(self):
        logger.debug(f'{bool(self.candidates)=}')
        if not self.candidates:
            return
        socialusers = SocialUser.objects.filter(
            user_id__in=[user.id for user in self.candidates]
        )
        try:
            community=self.socialuser.account.community
        except:
            community=None
        prospects = [
            Prospect(socialuser=su, community=community) for su in socialusers
        ]
        batch_size = len(prospects)
        Prospect.objects.bulk_create(
            prospects,
            batch_size,
            ignore_conflicts=True
        )

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

    def get_no_follow_back(self):
        try:
            friend = Friend.objects.filter(user=self.socialuser).latest("id")
        except Friend.DoesNotExist:
            logger.error(
                f'No Friend object for SocialUser {self.socialuser} was found'
            )
            return
        try:
            follower = Follower.objects.filter(user=self.socialuser).latest("id")
        except Follower.DoesNotExist:
            logger.error(
                f'No Follower object for SocialUser {self.socialuser} was found'
            )
            return
        friends_ids_set = set(friend.id_list)
        followers_ids_set = set(follower.id_list)
        candidates_ids_set = friends_ids_set - followers_ids_set
        for candidate_id in candidates_ids_set:
            self.candidates.append(User(candidate_id))

    def filter_since(self):
        self.candidates[:] = [
            user for user in self.candidates if self.process_delta(user)
        ]

    def filter_protected(self):
        self.create_update_profiles()
        protected_ids = SocialUser.objects.filter(
            user_id__in=[user.id for user in self.candidates],
            profile__json__protected = True
        ).values_list("user_id", flat=True)
        logger.debug(f'{protected_ids=}')
        self.candidates[:] = [
            user for user in self.candidates if user.id not in protected_ids
        ]

    def process_delta(self, user):
        if not user.since:
            return False
        delta_computed: timedelta = timezone.now() - user.since
        delta_limit = timedelta(days=self.delta)
        return delta_computed > delta_limit

    def friend_since(self):
        for user in self.candidates:
            try:
                latest_not_friend = Friend.objects \
                .filter(user=self.socialuser) \
                .exclude(id_list__contains=[user.id]) \
                .latest("id")
            except Friend.DoesNotExist:
                continue
            try:
                earliest_friend = Friend.objects \
                .filter(user=self.socialuser) \
                .filter(id_list__contains=[user.id]) \
                .filter(id__gte=latest_not_friend.id) \
                .earliest()
            except Friend.DoesNotExist:
                continue
            user.since = earliest_friend.created