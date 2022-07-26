import logging
import time
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
from twttr.models import UserActive
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
            force: bool = False,
            sample_size: Optional[int] = None,
            sleep: Optional[int] = None
        ):
        self.socialuser = socialuser
        self.friends: List[int] = self.get_friends()
        self.community = self.get_community()
        self.network: List[Community] = self.get_network()
        self.count = count
        self.api = self.get_api()
        self.candidates: List[User] = []
        self.delta = delta
        self.force = force
        self.sample_size = sample_size
        self.sleep = sleep or 60

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
        if self.sample_size:
            self.candidates[:]=self.random_sample(self.candidates)
        logger.debug(f'\n3. Count:{len(self.candidates)}\n{self.candidates}')
        self.friend_latest()
        logger.debug(f'\n4. Count:{len(self.candidates)}\n{self.candidates}')
        if self.delta:
            self.filter_latest()
        logger.debug(f'\n5. Count:{len(self.candidates)}\n{self.candidates}')
        self.order_latest()
        logger.debug(f'\n6. Count:{len(self.candidates)}\n{self.candidates}')
        # check follow_request: TODO: implement this when we upgrade Tweepy
        # to version >= 4.0
        logger.debug(f'\n7. Count:{len(self.candidates)}\n{self.candidates}')
        followed_dict = self.follow()
        logger.info(followed_dict)
        return followed_dict

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
        if self.sample_size > len(iterable) or self.sample_size < 0:
            return iterable
        return sample(
            iterable,
            self.sample_size
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

    def sample_candidates(self):
        sample, self.candidates = (
            self.candidates[:self.count], self.candidates[self.count:]
        )
        return sample

    def follow(self):
        if settings.DEBUG and not self.force:
            for user in self.candidates:
                logger.debug(f"{user} was followed.")
        else:
            followed_dict = {
                "candidates": len(self.candidates),
                "followed": 0    
            }
            follow_count = self.count
            while follow_count > 1:
                sample = self.sample_candidates()
                sample = self.filter_friendship(sample)
                for idx, user in enumerate(sample):
                    try:
                        response = self.api.create_friendship(
                            user_id=str(user.id)
                        )
                        if follow_count > 1:
                            time.sleep(self.sleep)
                        follow_count -= 1
                    except TweepError as e:
                        logger.error(e)
                        try:
                            sn = (
                                SocialUser.objects.get(user_id=user.id)
                                .screen_name_tag()
                            )
                        except SocialUser.DoesNotExist:
                            sn = "?"
                        followed_dict.update({
                            idx: {
                                'screen_name': sn,
                                'error': str(e)
                            }
                        })
                        try:
                            error_code =  e.args[0][0]['code']
                            self.process_error(error_code, user.id)
                            if error_code == 161:
                            #You are unable to follow more people at this time.
                                break
                        except:
                            pass
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
                else:
                    # Continue if the inner loop wasn't broken.
                    continue
                # Inner loop was broken, break the outer.
                break
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
        latest_inactive_ids = (
            UserActive.objects
            .filter(active=False)
            .order_by('socialuser__user_id', '-created')
            .distinct('socialuser__user_id')
            .values_list("socialuser__user_id", flat=True)
        )
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
            )
            .exclude(
                social_user__twitter_follow_request=self.socialuser,
                social_user__twitter_block=self.socialuser,
                social_user__user_id__in=latest_inactive_ids,
            )
            .values_list("social_user__user_id", flat=True)
        )
        logger.debug(f'{potential_members_ids=}')
        if self.sample_size and potential_members_ids:
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
        if self.sample_size and prospects_ids:
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

    def process_error(self, error_code, user_id):
        try:
            su = SocialUser.objects.get(user_id=user_id)
        except SocialUser.DoesNotExist:
            return
        #108 Cannot find specified user
        if (error_code==108):
            try:
                UserActive.objects.create(
                    active=False,
                    socialuser=su,
                )
            except:
                return
        #162 You have been blocked from following this account at the request of the user.
        elif (error_code==162):
            su.twitter_block.add(self.socialuser)
        #160 You've already requested to follow MadameProf1.
        elif (error_code==160):
            su.twitter_follow_request.add(self.socialuser)

    def filter_friendship(self, sample):
        filtered_sample=[]
        bot_id = self.socialuser.user_id
        for candidate in sample:
            try:
                friendship = self.api.show_friendship(
                    source_id=bot_id,
                    target_id=candidate.id
                )
            except TweepError as e:
                error_code =  e.args[0][0]['code']
                self.process_error(error_code, candidate.id)
                continue
            if friendship[0].blocked_by:
                try:
                    su = SocialUser.objects.get(user_id=candidate.id)
                except SocialUser.DoesNotExist:
                    continue
                su.twitter_block.add(self.socialuser)
                continue
            elif friendship[0].following_requested:
                try:
                    su = SocialUser.objects.get(user_id=candidate.id)
                except SocialUser.DoesNotExist:
                    continue
                su.twitter_follow_request.add(self.socialuser)
                continue
            filtered_sample.append(candidate)
        return filtered_sample