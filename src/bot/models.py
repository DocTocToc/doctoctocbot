from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

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
    launch = models.DateField(
        help_text="Launch date of the account",
        blank=True,
        default=None,
        null=True
    )
    backend_twitter_consumer_key = models.CharField(max_length=100)
    backend_twitter_consumer_secret = models.CharField(max_length=100)
    backend_twitter_access_token = models.CharField(max_length=100)
    backend_twitter_access_token_secret = models.CharField(max_length=100)
    password = models.CharField(
        max_length=128,
        blank=True
    )
    email = models.CharField(
        max_length=128,
        blank=True,
    )
    phone = PhoneNumberField(
        blank=True,
    )
    protected = models.BooleanField(
        default=False,
        help_text="Is this Twitter account protected (locked)?",
    )
    cookies = models.BinaryField(
        null=True,
        help_text = "Session cookies for Selenium"
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