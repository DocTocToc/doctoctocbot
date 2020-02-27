from django.db import models

from dublincore_resource.models import (
    AbstractDublinCoreResource,
    DublinCoreAgent,
)

class LociResource(AbstractDublinCoreResource):
    #dc:terms:isVersionOf/hasVersion
    is_version_of = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        related_name='hasVersion'
    )
    
class LociAgent(DublinCoreAgent):
    """ DublinCoreAgent:
    full_name = models.CharField(
        max_length=200
    )
    identifier = models.URLField(
        max_length=300, **FIELD_OPTIONAL
    )
    """
    url = models.URLField(
        blank=True,
        null=True,
    )
    
    