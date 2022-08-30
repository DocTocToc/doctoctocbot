from moderation.models import SocialUser
from bot.tweepy_api import get_api as get_tweepy_api
from tweepy import TweepError
from tweepy.models import User as TweepyUser
from community.models import Community
import logging
from community.helpers import get_community_twitter_tweepy_api
import time

logger = logging.getLogger(__name__)


class TwitterUser:
    
    def __init__(self, userid=None, socialuser=None):
        try:
            if userid and socialuser:
                if socialuser.user_id != userid:
                    raise ValueError("userid and socialuser.user_id mismatch!")
                self.id = userid
                self.socialuser = socialuser
            elif userid and not socialuser:
                try:
                    su = SocialUser.objects.get(user_id=userid)
                    self.id=userid
                    self.socialuser=su
                except SocialUser.DoesNotExist:
                    pass            
            elif not userid and socialuser:
                self.id = socialuser.user_id
                self.socialuser = socialuser
        except ValueError:
            pass
        
    def __str__(self):
        return f"TwitterUser id: {self.id}"

    def is_protected(self):
        try:
            protected = self.socialuser.profile.json.get("protected")
        except AttributeError:
            protected = None
        
        return protected
    
    def friend(self, community):
        if not isinstance(community, Community):
            logger.error(
                f"Given parameter {community} is not a Community object"
            )
            return
        api = get_community_twitter_tweepy_api(community)
        try:
            tweepy_user = api.create_friendship(user_id=self.id)
            logger.debug(tweepy_user)
            if isinstance(tweepy_user, TweepyUser):
                return True
        except TweepError as e:
            logger.error(e)
            return False

    def decline_follow_request(self, community):
        api = get_community_twitter_tweepy_api(community)
        resp = api.create_block(user_id=self.id)
        logger.debug(resp)
        time.sleep(5)
        resp = api.destroy_block(user_id=self.id)
        logger.debug(resp)

        
    