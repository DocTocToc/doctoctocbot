import logging

from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site

from community.models import Community

logger = logging.getLogger(__name__)

def get_community(context):
    site_id = get_current_site(context).id
    try:
        return Community.objects.get(site=site_id)
    except Community.DoesNotExist as e:
        logger.warn("No Community associated with context.", e)
        return