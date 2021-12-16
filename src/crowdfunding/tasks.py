import logging
from typing import Optional
from bot.tweepy_api import get_api
from celery import shared_task

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from crowdfunding.models import Project, Campaign, ProjectInvestment
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
    api = get_api(bot_screen_name, backend=True)    
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