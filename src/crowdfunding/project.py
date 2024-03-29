import logging
import datetime
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.utils import timezone
from crowdfunding.models import Project, ProjectInvestment, Campaign
from community.helpers import get_community

logger = logging.getLogger(__name__)


def get_project(request):
    community = get_community(request)
    if community:
        return community.crowdfunding

def get_campaign(request):
    project = get_project(request)
    now = timezone.now()
    try:
        return Campaign.objects.get(
            project=project,
            start_datetime__lte=now,
            end_datetime__gte=now,
        )
    except Campaign.DoesNotExist:
        return

def get_year_investor_count(context):
    project = get_project(context)
    logger.debug(project)
    year = context.get("year")
    start_date = get_project_year_start(project, year)
    end_date = get_project_year_end(project, year)
    count = ProjectInvestment.objects.filter(
        paid=True,
        project=get_project(context),
        datetime__gte=start_date,
        datetime__lt=end_date,
    ).distinct('user').count()
    logger.debug(f"type of 'count': {type(count)} count={count}")
    return count  

def get_year_public_investor_count(context):
    project = get_project(context)
    year = context.get("year")
    start_date = get_project_year_start(project, year)
    end_date = get_project_year_end(project, year)
    return ProjectInvestment.objects.filter(
        paid=True,
        public=True,
        project=project,
        datetime__gte=start_date,
        datetime__lt=end_date,
    ).distinct('user').count()

def get_year_private_investor_count(context):
    project = get_project(context)
    year = context.get("year")
    start_date = get_project_year_start(project, year)
    end_date = get_project_year_end(project, year)
    return ProjectInvestment.objects.filter(
        paid=True,
        public=False,
        datetime__gte=start_date,
        datetime__lt=end_date,
        project=project,
    ).distinct('user').count()

def get_project_year_start(project, year):
    if year is None:
        start_date = project.start_date
    else:
        start_date = project.start_date + relativedelta(years=year)
    return start_date
 
def get_project_year_end(project, year):
    if year is None:
        end_date = datetime.datetime.now()
    else:
        end_date = project.start_date + relativedelta(years=year+1)
    return end_date