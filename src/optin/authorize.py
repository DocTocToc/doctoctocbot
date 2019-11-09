import logging
from optin.models import OptIn, Option
from moderation.models import SocialUser
from django.db.utils import DatabaseError
from django.db import transaction
from typing import Optional

logger = logging.getLogger(__name__)

def has_authorized(socialuser: SocialUser, option: Option) -> Optional[bool]:
    if not option or not socialuser:
        return None
    if not isinstance(option, Option):
        logger.error("option is not an Option")
        return None
    if not isinstance(socialuser, SocialUser):
        logger.error("socialuser is not a SocialUser")
        return None
    try:
        optin = OptIn.objects.current.get(
            socialuser=socialuser,
            option=option
        )
        logger.debug(f"optin: {optin}")
    except OptIn.DoesNotExist as e:
        logger.error(e)
        return None
    if optin.authorize == None:
        logger.warn("{option} opt in status for {socialuser} is not set")
        return None
    logger.debug(f"{optin}")
    logger.debug(f"{optin.authorize}")
    return optin.authorize

def create_opt_in(socialuser: SocialUser, option: Option, authorize: bool = False) -> None:
    if not option or not socialuser:
        return
    if not isinstance(option, Option):
        logger.error("option is not an Option")
        return
    if not isinstance(socialuser, SocialUser):
        logger.error("socialuser is not a SocialUser")
        return
    # try to find a current pre-existing versioned OptIn
    try:
        with transaction.atomic():
            optin = OptIn.objects.current.get(
                socialuser=socialuser,
                option=option
            )
            optin = optin.clone()
            optin.authorize=authorize
            optin.save()
        return
    except OptIn.DoesNotExist as e:
        logger.error(e)
    try:
        with transaction.atomic():
            optin = OptIn.objects.create(
                socialuser=socialuser,
                option=option,
                authorize=authorize,
            )
            logger.debug(optin)
    except DatabaseError as e:
        logger.error(e)
    
    