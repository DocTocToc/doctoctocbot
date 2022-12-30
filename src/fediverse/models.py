from django.db import models
from django.contrib.postgres.fields import ArrayField

class MastodonInvitation(models.Model):
    uid = models.CharField(
        max_length=8,
        unique=True
    )
    socialuser = models.ForeignKey(
        'moderation.SocialUser',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    autofollow = models.ForeignKey(
        'moderation.MastodonUser',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    
    def __str__(self):
        return (
            f'MastodonInvitation {self.uid} {self.socialuser} '
            f'{self.autofollow}'
        )


    class Meta:
        unique_together = [['uid', 'socialuser']]


class MastodonScopesManager(models.Manager):
    def get_by_natural_key(self, scope):
        return self.get(scope=scope)


class MastodonScopes(models.Model):
    scope = models.CharField(
        max_length=255,
        unique=True,
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name= "children",
        null=True,
        blank=True,
    )
    description = models.CharField(
        max_length=255,
        blank=True,
    )

    objects = MastodonScopesManager()

    class Meta:
        verbose_name_plural = "Mastodon scopes"

    def __str__(self):
        return self.scope

    def natural_key(self):
        return (self.scope,)


class MastodonAppManager(models.Manager):
    def get_by_natural_key(self, client_name):
        return self.get(client_name=client_name)


class MastodonApp(models.Model):
    client_name = models.CharField(
        max_length=255,
        unique=True,
    )
    api_base_url=models.URLField()
    client_id = models.CharField(
        max_length=255,
        unique=True,
    )
    client_secret = models.CharField(
        max_length=255,
        unique=True,
    )
    website = models.URLField(
        max_length=255,
        null=True,
        blank=True
    )
    redirect_uris = ArrayField(
        models.URLField(),
        null=True,
        blank=True
    )
    scopes = models.ManyToManyField(
        'fediverse.MastodonScopes'
    )
    created = models.DateTimeField(auto_now_add=True)

    objects = MastodonAppManager()

    class Meta:
        pass

    def __str__(self):
        return self.client_name

    def natural_key(self):
        return (self.client_name,)


class MastodonAccess(models.Model):
    app = models.ForeignKey(
        'fediverse.MastodonApp',
        on_delete=models.CASCADE,
        related_name= "access",
    )
    user = models.ForeignKey(
        'moderation.MastodonUser',
        on_delete=models.CASCADE,
        related_name= "access",
    )
    access_token = models.CharField(
        max_length=255,
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Mastodon accesses"

    def __str__(self):
        return f'<{self.app.client_name} @{self.user.acct}>'


class Toot(models.Model):
    user=models.ForeignKey(
        'moderation.MastodonUser',
        on_delete=models.PROTECT,
        related_name= "toots",
    )
    uri_id=models.BigIntegerField()
    db_id=models.BigIntegerField(
        unique=True
    )
    created_at=models.DateTimeField()
    edited_at=models.DateTimeField(null=True)
    in_reply_to_id=models.BigIntegerField(null=True)
    in_reply_to_account_id=models.BigIntegerField(null=True)
    hashtag = models.ManyToManyField(
        'conversation.Hashtag',
        blank=True,
    )
    status=models.JSONField()
    reblogged_by = models.ManyToManyField(
        "moderation.MastodonUser",
        related_name = "reblogs",
        blank=True,
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    updated = models.DateTimeField(
        auto_now=True
    )


    class Meta:
        indexes = [
            models.Index(fields=['in_reply_to_id']),
            models.Index(fields=['in_reply_to_account_id'])
        ]


    def __str__(self):
        return f'<{self.db_id} {self.status["account"]["acct"]} {self.status["content"][:140]}>'