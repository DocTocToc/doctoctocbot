import logging
import random
from typing import Optional
from bot.tweepy_api import get_api
from celery import shared_task
from datetime import datetime
from django.db import DatabaseError
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from crowdfunding.models import Project, Campaign, ProjectInvestment
from moderation.models import SocialUser
from tweepy.error import TweepError

logger = logging.getLogger(__name__)

@shared_task
def handle_tweet_investment(
        userid: int,
        public: bool,
        project_id: Optional[int] = None,
        campaign_id: Optional[int] = None,
    ):
    #temporarily cancel tweeting about anonymous investments:
    if not public:
        return
    if not userid:
        return
    if not project_id or not campaign_id:
        return
    User = get_user_model()
    try:
        django_user = User.objects.get(id=userid)
    except User.DoesNotExist:
        return
    display_name = django_user.username
    try:
        display_name = "@" + django_user.social_auth.get(provider='twitter').extra_data.get('access_token').get('screen_name') 
    except ObjectDoesNotExist:
        pass
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        project = None
    try:
        campaign = Campaign.objects.get(id=campaign_id)
    except Campaign.DoesNotExist:
        campaign = None
    if campaign:
        rank = ProjectInvestment.objects.filter(
            campaign=campaign,
            paid=True,
        ).count()
    elif project:
        rank = ProjectInvestment.objects.filter(
            project=project,
            paid=True,
        ).count()
    community = project.community
    bot_screen_name = community.account.username
    domain_name = community.site.domain
    api = get_api(username=bot_screen_name)    
    if public:
        status = (
            "Merci à {display_name} pour sa participation "
            "à ma campagne de financement! 🤖 "
            "Vous pouvez consulter la liste des dépenses "
            "et des projets en cours de développement et y contribuer ici ⬇️ "
            "https://{domain_name}/financement/"
            .format(
                display_name=display_name,
                domain_name=domain_name,
            )
        )
    elif not public:
        status = (
            "Merci à la personne qui vient de faire la {rank}ème contribution "
            "à ma campagne de financement! 🤖 "
            "Cette personne a souhaité garder l'anonymat. "
            "Vous pouvez consulter la liste des dépenses "
            "et des projets en cours de développement et y contribuer ici ⬇️ "
            "https://{domain_name}/financement/"
            .format(
                rank=rank,
                domain_name=domain_name,
            )
        )
    try:
        api.update_status(status)
    except TweepError as e:
        logger.error(f"Error creating status update: {e}")
        return
    except AttributeError:
        logger.error(f"{api=}")
        return

@shared_task
def handle_add_campaign(
        uuid: str
    ):
    """add the correct Campaign field to a ProjectInvestment object.
    """
    if not isinstance(uuid, str):
        logger.error(f'{uuid} is not an instance of str')
        return
    try:
        pi=ProjectInvestment.objects.get(uuid=uuid)
    except ProjectInvestment.DoesNotExist as e:
        logger.error(f'ProjectInvestment {uuid} does not exist.\n{e}')
        return
    if pi.campaign:
        logger.debug(
            f'ProjectInvestment {pi} '
            f'already has a Campaign field: {pi.campaign}'
        )
        return
    user = pi.user
    if not user:
        return
    social_user: list = []
    for social_auth in user.social_auth.filter(provider='twitter'):
        for su in SocialUser.objects.filter(user_id=social_auth.uid):
            social_user.append(su)
    if not social_user:
        su = user.socialuser
        if su:
            social_user.append(su)
    if not social_user:
        add_campaign_from_project(uuid)
        return
    social_user.sort(key=lambda x: x.user_id, reverse=True)
    try:
        su = social_user[0]
    except IndexError:
        return
    project_qs = Project.objects.filter(
        community__membership__id__in=[su.category.values_list('id',flat=True)]
    )
    if not project_qs or pi.project in project_qs:
        add_campaign_from_project(uuid)
        return
    else:
        project=random.choice(project_qs)
        pi.project = project
        pi.campaign=get_campaign(pi)
        try:
            pi.save()
        except DatabaseError as e:
            logger.error(f'{e}')

def get_campaign(pi: ProjectInvestment):
    return Campaign.objects.filter(
        project=pi.project,
        start_datetime__lte=pi.datetime,
        end_datetime__gte=pi.datetime,
    ).order_by('id').last()

def add_campaign_from_project(uuid):
    """add the correct Campaign field to a ProjectInvestment object.
    """
    try:
        pi=ProjectInvestment.objects.get(uuid=uuid)
    except ProjectInvestment.DoesNotExist as e:
        logger.error(f'ProjectInvestment {uuid} does not exist.\n{e}')
        return
    pi.campaign=get_campaign(pi)
    try:
        pi.save()
    except DatabaseError as e:
        logger.error(f'{e}')