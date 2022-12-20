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
    website = models.CharField(
        max_length=255,
    )
    redirect_uris = ArrayField(
        models.URLField()
    )
    created = models.DateTimeField(auto_now_add=True)

    objects = MastodonAppManager()

    class Meta:
        pass

    def __str__(self):
        return self.client_name

    def natural_key(self):
        return (self.client_name,)