from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from moderation.models import SocialUser


class User(AbstractUser):
    socialuser = models.ForeignKey(SocialUser,
                                   blank=True,
                                   null=True,
                                   default=None,
                                   on_delete=models.CASCADE,)
    
    def __str__(self):
        return self.username
