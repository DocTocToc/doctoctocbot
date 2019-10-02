import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from crowdfunding.models import Project, ProjectInvestment
from community.helpers import get_community


logger = logging.getLogger(__name__)


def get_project(request):
    try:
        return Project.objects.get(name=settings.PROJECT_NAME)
    except (AttributeError, ImproperlyConfigured, Project.DoesNotExist):
        community = get_community(request)
        if community:
            return community.crowdfunding
        
def get_total_investor_count(request):
    project = get_project(request)
    logger.debug(project)
    count = ProjectInvestment.objects.filter(
        paid=True,
        project=get_project(request)
    ).distinct('user').count()
    logger.debug(f"type of 'count': {type(count)} count={count}")
    return count  
    
    
def get_public_investor_count(request):
    return ProjectInvestment.objects.filter(
        paid=True,
        public=True,
        project=get_project(request)
    ).distinct('user').count()
    
def get_private_investor_count(request):
    return ProjectInvestment.objects.filter(
        paid=True,
        public=False,
        project=get_project(request)
    ).distinct('user').count()
