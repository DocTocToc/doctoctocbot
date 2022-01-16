from community.models import Community
from moderation.models import SocialUser, Friend, Queue
from bot.lib.datetime import get_datetime_tz_from_twitter_str
from django.utils import timezone
from community.helpers import get_community_member_friend
from moderation.moderate import create_initial_moderation

class User:
    def __init__(self, socialuser: SocialUser):
        self.socialuser = socialuser

    def is_protected(self):
        try:
            return self.socialuser.profile.json["protected"]
        except:
            return

    def is_friend(self, bot):
        try:
            friend = Friend.objects.filter(user=bot).latest('id')
        except Friend.DoesNotExist:
            return 
        return self.socialuser.user_id in friend.id_list

    def followers_count(self):
        try:
            return self.socialuser.profile.json["followers_count"]
        except:
            return
        
    def member_follower_count(self, community: Community):
        cnt = get_community_member_friend(community)
        return cnt[self.socialuser.user_id]

    def statuses_count(self):
        try:
            return self.socialuser.profile.json["statuses_count"]
        except:
            return

    def has_default_profile_image(self):
        try:
            return self.socialuser.profile.json["default_profile_image"]
        except:
            return

    def account_age(self):
        try:
            created_at = self.socialuser.profile.json["created_at"]
        except:
            return
        creation_dt = get_datetime_tz_from_twitter_str(created_at)
        return timezone.now() - creation_dt


class QueueFilter:
    def __init__(self, community: Community, socialuser: SocialUser):
        self.community = community
        self.bot = community.account.socialuser
        self.user = User(socialuser)
        self.filter = community.moderation_filter

    def access_protected(self):
        if not self.filter.access_protected:
            return True
        elif not self.user.is_protected():
            return True
        elif self.user.is_friend(self.bot):
            return True
        else:
            return False

    def followers_count(self):
        if not self.filter.followers_count:
            return True
        else:
            return self.user.followers_count() >= self.filter.followers_count

    def member_follower_count(self):
        if not self.filter.member_follower_count:
            return True
        else:
            return (
                self.user.member_follower_count(self.filter.community)
                >=
                self.filter.member_follower_count
            )

    def statuses_count(self):
        if not self.filter.statuses_count:
            return True
        else:
            return self.user.statuses_count() >= self.filter.statuses_count

    def profile_image(self):
        if not self.filter.profile_image:
            return True
        else:
            return not self.user.has_default_profile_image()

    def account_age(self):
        filter_age = self.filter.account_age
        if not filter_age:
            return True
        age = self.user.account_age()
        if not age:
            return True
        return age >= filter_age  

    def start_moderation(self):
        return (
            self.access_protected()
            and self.followers_count()
            and self.statuses_count()
            and self.profile_image()
            and self.account_age()
            and self.member_follower_count()
        )


def process_onhold_queues(community: Community):
    for queue in Queue.objects.current.filter(
        community=community,
        type=Queue.ONHOLD,
    ):
        try:
            socialuser=SocialUser.objects.get(user_id=queue.user_id)
        except SocialUser.DoesNotExist:
            continue
        qf=QueueFilter(community, socialuser)
        if qf.start_moderation():
            if qf.user.member_follower_count(community):
                queue = queue.clone()
                queue.type=Queue.FOLLOWER
                queue.save()
            else:
                queue = queue.clone()
                queue.type=Queue.MODERATOR
                queue.save()
            create_initial_moderation(queue.refresh_from_db())
                
        
            