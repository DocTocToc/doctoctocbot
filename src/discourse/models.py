from django.db import models
from moderation.models import Category


class AccessControl(models.Model):
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
    