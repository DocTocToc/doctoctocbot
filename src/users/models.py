from django.contrib.auth.models import AbstractUser
from django.db import models
from moderation.models import Entity

from moderation.models import SocialUser


class User(AbstractUser):
    socialuser = models.ForeignKey(
        SocialUser,
        blank=True,
        null=True,
        default=None,
        on_delete=models.CASCADE,
    )
    entity = models.ForeignKey(
        Entity,
        blank=True,
        null=True,
        default=None,
        on_delete=models.PROTECT,
    )
    
    def __str__(self):
        return f'{self.id} - {self.username}'

    def is_categorized(self) -> bool:
        """Does this Django user belong to a category?
        """
        try:
            user_categories = self.socialuser.category.all()
            return bool(user_categories)
        except:
            return False
        
    def get_user_api_access(self):
        pass
