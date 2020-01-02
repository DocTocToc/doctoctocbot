from bot.python_twitter_api import get_api

def get_incoming_friendship(community):
    try:
        screen_name=community.account.username
    except:
        return []
    api = get_api(screen_name)
    return api.IncomingFriendship()