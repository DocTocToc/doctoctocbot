from django.db import models
from django.contrib.postgres.fields import ArrayField

class Word(models.Model):
    """Words represent variables containing list of strings used in Filters
    These variables are instanciated before the evaluation of expressions.
    """
    name = models.CharField(
        max_length=79,
        unique=True,
        help_text = "Valid variable name"
    )
    word = ArrayField(
        models.CharField(max_length=255, blank=True)
    )

    def __str__(self):
        return self.name

class Filter(models.Model):
    name = models.CharField(
        max_length=79,
        unique=True,
        help_text = "Valid variable name",
    )
    active = models.BooleanField(
        default=True,
        help_text = "Is this filter activated?",
    )
    community = models.ManyToManyField(
        'community.Community',
        blank=True,
        help_text = ("This filter will be applied to these communities.")
    )
    expression = models.TextField(
        help_text = (
        "Python expression returning a boolean."
        )
    )
    word = models.ManyToManyField(
        Word,
        blank=True,
        help_text = ("Word objects used in the expression.")
    )   
    
    def __str__(self):
        return self.name