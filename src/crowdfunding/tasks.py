from bot.twitter import get_api
from doctocnet.celery import app
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

@app.task
def handle_tweet_investment(userid: int,
                            rank: int,
                            public: bool):
    
    if not rank or not userid:
        return
    
    User = get_user_model()
    
    try:
        django_user = User.objects.get(userid)
    except User.DoesNotExist:
        return
    
    display_name = django_user.username
    
    try:
        display_name = django_user.social_auth.get(provider='twitter').extra_data.get('access_token').get('screen_name') 
    except ObjectDoesNotExist:
        pass
    
    api = get_api()
    if public:
        status = (
            "Merci à {display_name} pour sa participation "
            "à ma campagne de financement 2019! 🤖 "
            "Vous pouvez consulter la liste des dépenses "
            "et des projets en cours de développement et y contribuer ici ⬇️ "
            "https://doctoctoc.net/financement/"
            .format(display_name=display_name)
        )
    elif not public:
        status = (
            "Merci à la personne qui vient de faire la {rank}ème contribution "
            "à ma campagne de financement 2019! 🤖 "
            "Cette personne a souhaité garder l'anonymat. "
            "Vous pouvez consulter la liste des dépenses "
            "et des projets en cours de développement et y contribuer ici ⬇️ "
            "https://doctoctoc.net/financement/"
            .format(rank=rank)
        )        
    api.update_status(status)