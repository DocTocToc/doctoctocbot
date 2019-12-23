from django.db import models

from versions.models import Versionable
#from versions.fields import VersionedForeignKey


class OptIn(Versionable):
    option = models.ForeignKey(
        'optin.Option',
        on_delete=models.CASCADE,
        related_name='optin')
    socialuser = models.ForeignKey(
        'moderation.SocialUser',
        on_delete=models.CASCADE,
        related_name='optin')
    authorize = models.BooleanField(
        default=None
    )
    
    def __str__(self):
        return(f"{self.option}, {self.socialuser}, {self.authorize}")


class Option(models.Model):
    name = models.CharField(max_length=255, unique=True)
    label = models.CharField(max_length=255, null=True)
    description = models.TextField(blank=True, null=True)
    default_bool = models.BooleanField(
        null=True
    )
    
    def __str__(self):
        return(f"{self.name}")