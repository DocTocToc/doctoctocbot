import logging

from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site
from django.db.utils import DatabaseError

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
    except DatabaseError:
        return
    except Community.DoesNotExist:
        try:
            site = Site.objects.first()
            if site:
                return Community.objects.get(site=site.id)
        except Community.DoesNotExist as e:
            logger.warn("Create at least one community. %s", e)