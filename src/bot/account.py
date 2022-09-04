import random
import logging
from bot.models import Account

logger = logging.getLogger(__name__)

def random_bot_username():
    usernames = list(
        Account.objects \
        .filter(active=True) \
        .values_list("username", flat=True)
    )
    try:
        return random.choice(usernames)
    except IndexError as e:
        logger.error(e)
        return