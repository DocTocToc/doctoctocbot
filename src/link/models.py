from django.db import models
from conversation.models import Tweetdj
from moderation.models import SocialUser 

class Website(models.Model):
    network_location = models.CharField(
        max_length=255,
        unique=True
    )

    def __str__(self):
        return self.network_location


class Link(models.Model):
    url = models.CharField(
        unique=True,
        max_length=255
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.PROTECT,
        related_name = 'links',
    )
    status = models.ManyToManyField(Tweetdj)
    socialuser = models.ManyToManyField(SocialUser)
    
    def __str__(self):
        return "{0} ; {1}".format(self.url, self.website)
