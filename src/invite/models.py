from django.db import models
from django.utils.crypto import get_random_string
from invitations.models import Invitation
from moderation.models import Category


class CategoryInvitation(Invitation):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
    )
    
    @classmethod
    def create(cls, email, category=None, inviter=None, **kwargs):
        key = get_random_string(64).lower()
        instance = cls._default_manager.create(
            email=email,
            key=key,
            inviter=inviter,
            category=category,
            **kwargs)
        return instance