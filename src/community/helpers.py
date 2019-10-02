import logging

from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site

from community.models import Community

logger = logging.getLogger(__name__)

def get_community(request):
    """
    Return a Community object or None given the request.
    """
    site = get_current_site(request)
    if not site:
        return
    try:
        return Community.objects.get(site=site.id)
    except Community.DoesNotExist as e:
        logger.warn(e)
        try:
            return Community.objects.get(site=1)
        except Community.DoesNotExist as e:
            logger.warn("Create at least one community.", e)