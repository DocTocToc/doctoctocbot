from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class AccountManager(models.Manager):
    def get_by_natural_key(self, user_id):
        return self.get(userid=user_id)


class Account(models.Model):
    userid = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=15)
    socialuser = models.OneToOneField(
        'moderation.SocialUser',
        on_delete=models.PROTECT,
        null=True,
    )
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
    twitter_consumer_key = models.CharField(max_length=100)
    twitter_consumer_secret = models.CharField(max_length=100)
    twitter_access_token = models.CharField(max_length=100)
    twitter_access_token_secret = models.CharField(max_length=100)
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
    objects = AccountManager()

    def __str__(self):
        return self.username

    def natural_key(self):
        return (self.userid,)


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


class TwitterAppManager(models.Manager):
    def get_by_natural_key(self, app_id):
        return self.get(app_id=app_id)


class TwitterApp(models.Model):
    app_id = models.PositiveBigIntegerField()
    name = models.CharField(
        max_length=255,
        blank=True,
    )
    description = models.TextField(
        blank=True
    )
    consumer_key = models.CharField(
        max_length=255,
        blank=True,
    )
    consumer_secret = models.CharField(
        max_length=255,
        blank=True,
    )
    bearer_token = models.CharField(
        max_length=255,
        blank=True,
    )
    client_id = models.CharField(
        max_length=255,
        blank=True,
    )
    client_secret = models.CharField(
        max_length=255,
        blank=True,
    )
    redirect_uri = models.CharField(
        max_length=255,
        blank=True,
    )
    api = models.ForeignKey(
        'bot.TwitterAPI',
        null = True,
        blank = True,
        on_delete = models.PROTECT,
    )
    scopes = models.ManyToManyField(
        'bot.TwitterScopes'
    )

    objects = TwitterAppManager()

    def __str__(self):
        return f'{self.id}, {self.name}'

    def natural_key(self):
        return (self.app_id,)


class TwitterAPIManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class TwitterAPI(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
    )

    objects = TwitterAPIManager()

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)


class TwitterScopesManager(models.Manager):
    def get_by_natural_key(self, scope):
        return self.get(scope=scope)


class TwitterScopes(models.Model):
    scope = models.CharField(
        max_length=255,
        unique=True,
    )
    description = models.CharField(
        max_length=255,
        blank=True,
    )

    objects = TwitterScopesManager()

    def __str__(self):
        return self.scope

    def natural_key(self):
        return (self.scope,)


class AccessToken(models.Model):

    class OAuth(models.TextChoices):
        OAUTH1 = 'O1', 'OAuth 1.0a'
        OAUTH2 = 'O2', 'OAuth 2.0'

    oauth = models.CharField(
        max_length=2,
        choices=OAuth.choices,
        default=OAuth.OAUTH2,
    )
    account = models.ForeignKey(
        'bot.Account',
        on_delete = models.PROTECT,
    )
    app = models.ForeignKey(
        'bot.TwitterApp',
        on_delete = models.PROTECT,
    )
    token = models.JSONField(
        blank=True,
        null=True,
    )
    created =  models.DateTimeField(auto_now_add=True)
    updated =  models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'account: {self.account} app: {self.app} oauth: {self.oauth}'