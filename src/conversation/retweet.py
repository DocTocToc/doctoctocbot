from conversation.models import Tweetdj
from moderation.models import SocialUser

def add_retweeted_by(statusid, userid, by_socialuserid ):
    status, _ = Tweetdj.objects.get_or_create(
        statusid=statusid,
        userid=userid
    )
    status.save()
    status.retweeted_by.add(by_socialuserid)

def add_quoted_by(statusid, userid, by_socialuserid ):
    status, _ = Tweetdj.objects.get_or_create(
        statusid=statusid,
        userid=userid
    )
    status.save()
    status.quoted_by.add(by_socialuserid)


class RetweetedBy:
    def __init__(self, socialuser: SocialUser, batch: int):
        self.socialuser = socialuser
        self.batch = batch
        self.retweets_qs = self.get_retweets_qs()

    def count(self):
        return Tweetdj.objects.filter(retweeted_by=self.socialuser).count()

    def get_retweets_qs(self):
        return Tweetdj.objects.filter(
            retweetedstatus=True,
            json__isnull=False,
            socialuser=self.socialuser,
        ).order_by('-statusid')

    def process(self):
        for i in range(0, self.retweets_qs.count(), self.batch):
            for status in self.retweets_qs[i:i+self.batch]:
                try:
                    statusid = status.json["retweeted_status"]["id"]
                except KeyError:
                    continue
                try:
                    userid = status.json["retweeted_status"]["user"]["id"]
                except KeyError:
                    continue
                add_retweeted_by(
                    statusid = statusid,
                    userid = userid,
                    by_socialuserid = self.socialuser.id,
                )