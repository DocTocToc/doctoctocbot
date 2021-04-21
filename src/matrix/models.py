from django.db import models
from moderation.models import Category
from community.models import Community


class CategoryAccessControl(models.Model):
    category = models.OneToOneField(
        Category,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    authorize = models.BooleanField(default=False)

    def __str__(self):
        return "Category {category}; authorize: {authorize}".format(
            category=self.category.name,
            authorize=self.authorize
        )


class CommunityAccessControl(models.Model):
    community = models.OneToOneField(
        Community,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='matrix'
    )
    authorize = models.BooleanField(default=False)

    def __str__(self):
        return "CommunityAccessControl: community {community}; authorize: {authorize}".format(
            community=self.community.name,
            authorize=self.authorize
        )