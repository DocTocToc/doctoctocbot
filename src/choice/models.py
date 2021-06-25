from django.db import models
from django.contrib.gis.db import models as gismodels


class School(models.Model):
    tag = models.CharField(max_length=255, blank=False)
    name = models.CharField(max_length=255, blank=False)
    university = models.CharField(max_length=255, blank=False)
    geometry = gismodels.PointField()

    class Meta:
        # order of drop-down list items
        ordering = ('tag',)
