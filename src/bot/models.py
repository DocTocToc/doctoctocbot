from django.db import models


class Account(models.Model):
    userid = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=15)
    twitter_consumer_key = models.CharField(max_length=100)
    twitter_consumer_secret = models.CharField(max_length=100)
    twitter_access_token = models.CharField(max_length=100)
    twitter_access_token_secret = models.CharField(max_length=100)
    active = models.BooleanField(default=False)
    hashtag = models.ManyToManyField(
        "conversation.Hashtag",
        blank=True    
    )
    
    def __str__(self):
        return self.username


class Greet(models.Model):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
    )
    active = models.BooleanField(default=False)
    campaign = models.ForeignKey(
        "messenger.Campaign",
        on_delete=models.CASCADE,
    )
    
    def __str__(self):
        return "{} {}".format(self.account.username, self.campaing.name)