from bot.twitter import get_api
from celery import shared_task

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from crowdfunding.models import Project

@shared_task
def handle_tweet_investment(userid: int,
                            rank: int,
                            public: bool,
                            project_id: int):
    
    if (not rank
        or not userid
        or not project_id):
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
        return
    community = project.community.get()
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
    api.update_status(status)