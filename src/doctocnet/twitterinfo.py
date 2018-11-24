import logging
logger = logging.getLogger(__name__)

def show_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'twitter':
        logger.debug(f"backend: {backend}")
        logger.debug(f"user: {user}")
        try:
            if user.id is not None:
                logger.debug(f"user.id: {user.id}")
        except:
            pass
        logger.debug(f"response: {str(response)[:140]}")
        logger.debug(f"args: {args}")
        logger.debug(f"kwargs: {kwargs}")
        logger.debug(f"uid: {kwargs['uid']}")



