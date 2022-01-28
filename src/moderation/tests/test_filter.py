from django.test import TestCase, Client
from model_bakery import baker
from moderation.filter import User, QueueFilter
from pprint import pprint
import mock
from collections import Counter
from decimal import *


class TestUserFollowersCount(TestCase):
    def setUp(self):
        self.profile = baker.make(
            'moderation.Profile',
            json = {"followers_count": 0}
        )
        self.user = User(self.profile.socialuser)

    def test_followers_count(self):
        assert self.user.followers_count() == 0


class TestQueueFilterFollowersCount(TestCase):
    def setUp(self):
        pass

    def test_qf_0_fc_0(self):
        filter = baker.make(
            'moderation.Filter',
            followers_count=0,
        )
        community = filter.community
        profile = baker.make(
            'moderation.Profile',
            json = {"followers_count": 0}
        )
        socialuser = profile.socialuser
        qf=QueueFilter(community, socialuser)
        assert qf.followers_count() is True


    def test_qf_0_fc_1(self):
        filter = baker.make(
            'moderation.Filter',
            followers_count=0,
        )
        community = filter.community
        profile = baker.make(
            'moderation.Profile',
            json = {"followers_count": 1}
        )
        socialuser = profile.socialuser
        qf=QueueFilter(community, socialuser)
        assert qf.followers_count() is True

    def test_qf_1_fc_0(self):
        filter = baker.make(
            'moderation.Filter',
            followers_count=1,
        )
        community = filter.community
        profile = baker.make(
            'moderation.Profile',
            json = {"followers_count": 0}
        )
        socialuser = profile.socialuser
        qf=QueueFilter(community, socialuser)
        assert qf.followers_count() is False
        
    def test_qf_1_fc_1(self):
        filter = baker.make(
            'moderation.Filter',
            followers_count=1,
        )
        community = filter.community
        profile = baker.make(
            'moderation.Profile',
            json = {"followers_count": 1}
        )
        socialuser = profile.socialuser
        qf=QueueFilter(community, socialuser)
        assert qf.followers_count() is True

    def test_qf_1_fc_2(self):
        filter = baker.make(
            'moderation.Filter',
            followers_count=1,
        )
        community = filter.community
        profile = baker.make(
            'moderation.Profile',
            json = {"followers_count": 2}
        )
        socialuser = profile.socialuser
        qf=QueueFilter(community, socialuser)
        assert qf.followers_count() is True


@mock.patch("moderation.filter.get_community_member_friend")
class TestQueueFilterMemberFollowerCount(TestCase):
    
    def setUp(self):
        pass
    
    def test_qfmfc_0_sumfc_0(self, mock_get_community_member_friend):
        filter = baker.make(
            'moderation.Filter',
            member_follower_count=0,
        )
        community = filter.community
        socialuser = baker.make(
            'moderation.socialuser',
        )
        key = socialuser.user_id
        value = 0
        mock_get_community_member_friend.return_value=Counter({key: value})
        qf=QueueFilter(community, socialuser)
        assert qf.member_follower_count() is True
        
    def test_qfmfc_0_sumfc_1(self, mock_get_community_member_friend):
        filter = baker.make(
            'moderation.Filter',
            member_follower_count=0,
        )
        community = filter.community
        socialuser = baker.make(
            'moderation.socialuser',
        )
        key = socialuser.user_id
        value = 1
        mock_get_community_member_friend.return_value=Counter({key: value})
        qf=QueueFilter(community, socialuser)
        assert qf.member_follower_count() is True
        
    def test_qfmfc_1_sumfc_0(self, mock_get_community_member_friend):
        filter = baker.make(
            'moderation.Filter',
            member_follower_count=1,
        )
        community = filter.community
        socialuser = baker.make(
            'moderation.socialuser',
        )
        key = socialuser.user_id
        value = 0
        mock_get_community_member_friend.return_value=Counter({key: value})
        qf=QueueFilter(community, socialuser)
        assert qf.member_follower_count() is False
        
    def test_qfmfc_1_sumfc_1(self, mock_get_community_member_friend):
        filter = baker.make(
            'moderation.Filter',
            member_follower_count=1,
        )
        community = filter.community
        socialuser = baker.make(
            'moderation.socialuser',
        )
        key = socialuser.user_id
        value = 1
        mock_get_community_member_friend.return_value=Counter({key: value})
        qf=QueueFilter(community, socialuser)
        assert qf.member_follower_count() is True
        
    def test_qfmfc_1_sumfc_2(self, mock_get_community_member_friend):
        filter = baker.make(
            'moderation.Filter',
            member_follower_count=1,
        )
        community = filter.community
        socialuser = baker.make(
            'moderation.socialuser',
        )
        key = socialuser.user_id
        value = 2
        mock_get_community_member_friend.return_value=Counter({key: value})
        qf=QueueFilter(community, socialuser)
        assert qf.member_follower_count() is True
        

@mock.patch("moderation.filter.get_community_member_friend")
class TestQueueFilterMemberFollowerRatio(TestCase):

    def setUp(self):
        pass

    def test_qfmfr_0_sufc_0_sumfc_0(self, mock_get_community_member_friend):
        filter = baker.make(
            'moderation.Filter',
            member_follower_ratio=0,
        )
        community = filter.community
        profile = baker.make(
            'moderation.Profile',
            json = {"followers_count": 0}
        )
        socialuser = profile.socialuser
        key = socialuser.user_id
        value = 0
        mock_get_community_member_friend.return_value=Counter({key: value})
        qf=QueueFilter(community, socialuser)
        assert qf.member_follower_ratio() is True
        
    def test_qfmfr_0_sufc_1_sumfc_0(self, mock_get_community_member_friend):
        filter = baker.make(
            'moderation.Filter',
            member_follower_ratio=0,
        )
        community = filter.community
        profile = baker.make(
            'moderation.Profile',
            json = {"followers_count": 1}
        )
        socialuser = profile.socialuser
        key = socialuser.user_id
        value = 0
        mock_get_community_member_friend.return_value=Counter({key: value})
        qf=QueueFilter(community, socialuser)
        assert qf.member_follower_ratio() is True
        
    def test_qfmfr_0_sufc_1_sumfc_1(self, mock_get_community_member_friend):
        filter = baker.make(
            'moderation.Filter',
            member_follower_ratio=0,
        )
        community = filter.community
        profile = baker.make(
            'moderation.Profile',
            json = {"followers_count": 1}
        )
        socialuser = profile.socialuser
        key = socialuser.user_id
        value = 1
        mock_get_community_member_friend.return_value=Counter({key: value})
        qf=QueueFilter(community, socialuser)
        assert qf.member_follower_ratio() is True
        
    def test_qfmfr_sufc_0_sumfc_0(self, mock_get_community_member_friend):
        filter = baker.make(
            'moderation.Filter',
            member_follower_ratio=0.5,
        )
        community = filter.community
        profile = baker.make(
            'moderation.Profile',
            json = {"followers_count": 0}
        )
        socialuser = profile.socialuser
        key = socialuser.user_id
        value = 0
        mock_get_community_member_friend.return_value=Counter({key: value})
        qf=QueueFilter(community, socialuser)
        assert qf.member_follower_ratio() is False
        
    def test_qfmfr_sufc_1_sumfc_0(self, mock_get_community_member_friend):
        filter = baker.make(
            'moderation.Filter',
            member_follower_ratio=0.5,
        )
        community = filter.community
        profile = baker.make(
            'moderation.Profile',
            json = {"followers_count": 1}
        )
        socialuser = profile.socialuser
        key = socialuser.user_id
        value = 0
        mock_get_community_member_friend.return_value=Counter({key: value})
        qf=QueueFilter(community, socialuser)
        assert qf.member_follower_ratio() is False
    
    def test_qfmfr_equal_sumfr(self, mock_get_community_member_friend):
        filter = baker.make(
            'moderation.Filter',
            member_follower_ratio=Decimal(0.5),
        )
        community = filter.community
        profile = baker.make(
            'moderation.Profile',
            json = {"followers_count": 2}
        )
        socialuser = profile.socialuser
        key = socialuser.user_id
        value = 1
        mock_get_community_member_friend.return_value=Counter({key: value})
        qf=QueueFilter(community, socialuser)
        assert qf.member_follower_ratio() is True
        
    def test_qfmfr_gte_sumfr(self, mock_get_community_member_friend):
        filter = baker.make(
            'moderation.Filter',
            member_follower_ratio=Decimal(0.6),
        )
        community = filter.community
        profile = baker.make(
            'moderation.Profile',
            json = {"followers_count": 2}
        )
        socialuser = profile.socialuser
        key = socialuser.user_id
        value = 1
        mock_get_community_member_friend.return_value=Counter({key: value})
        qf=QueueFilter(community, socialuser)
        assert qf.member_follower_ratio() is False


    def test_qfmfr_lte_sumfr(self, mock_get_community_member_friend):
        filter = baker.make(
            'moderation.Filter',
            member_follower_ratio=Decimal(0.4),
        )
        community = filter.community
        profile = baker.make(
            'moderation.Profile',
            json = {"followers_count": 2}
        )
        socialuser = profile.socialuser
        key = socialuser.user_id
        value = 1
        mock_get_community_member_friend.return_value=Counter({key: value})
        qf=QueueFilter(community, socialuser)
        assert qf.member_follower_ratio() is True