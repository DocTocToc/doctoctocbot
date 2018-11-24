import os
import inspect
import json
import logging
from django.conf import settings

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def getConfig():                                                        
    """
    Get config object.
    To use production configuration file, export environment variables:
    # Without this environment variable, defaults to configtest.json
    BOT_DEBUG=False
    """
    #BOT_ENV = os.environ.get('BOT_ENV', None)
    logger.debug(f"DEBUG={settings.DEBUG}")
    if settings.DEBUG is True:
        configfilename = "configtest.json"
    else:
        configfilename = "configprod.json"
    
    path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    configfilepath = os.path.join(path, configfilename)
    #config = configparser.SafeConfigParser()
    #config.read(configfilepath)
    config = json.load(open(configfilepath))
    
    #add env variables
    secret_dict = {
        'consumer_key': 'TWITTER_CONSUMER_KEY',
        'consumer_secret': 'TWITTER_CONSUMER_SECRET',
        'access_token': 'TWITTER_ACCESS_TOKEN',
        'access_token_secret': 'TWITTER_ACCESS_TOKEN_SECRET',
    }
    
    if settings.DEBUG is True:
        suffix = '_DOC_TEST'
    else:
        suffix = '_DOC_PROD'
    
    for key in secret_dict.keys():
        secret_dict[key] = secret_dict[key] + suffix
        config['twitter'][key] = os.environ.get(secret_dict[key])

    return config

if __name__ == "__main__":
    logger.debug(os.environ.get('TWITTER_CONSUMER_KEY_DOC_PROD'))
    getConfig()