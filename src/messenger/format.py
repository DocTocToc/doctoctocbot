from moderation.models import SocialUser
from community.models import Community
from conversation.models import Tweetdj
from community.helpers import activate_language
from django.utils.formats import date_format

class FormatManager:
    def __init__(
            self,
            template: str,
            recipient: SocialUser,
            sender: SocialUser,
            community: Community,
    ):
        self.template = template
        self.recipient = recipient
        self.sender = sender
        self.retweeted_qs = Tweetdj.objects.filter(
            retweeted_by=self.sender,
            socialuser=self.recipient,
        )
        self.community = community

    def first_retweet_date(self) -> str:
        if self.community:
            activate_language(self.community)
        try:
            dt = self.retweeted_qs.earliest('statusid').created_at
            return date_format(dt, format='DATE_FORMAT', use_l10n=True)
        except Tweetdj.DoesNotExist:
            return

    def format(self):
        d = {
            'screen_name' : self.recipient.profile.screen_name_tag(),
            'sender_screen_name' : self.sender.profile.screen_name_tag(),
            'retweet_count' : self.retweeted_qs.count(),
            'first_retweet_date' : self.first_retweet_date(),
            'community' : self.community.name,
        }
        return self.template.format(**d)