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
    You must set these environment variables:
    'TWITTER_CONSUMER_KEY', 'TWITTER_CONSUMER_SECRET', 'TWITTER_ACCESS_TOKEN',
    TWITTER_ACCESS_TOKEN_SECRET'
    You can set them programmatically with Python in your settings file or
    through your .bashrc file
    """
    if settings.DEBUG is True:
        configfilename = "configtest.json"
    else:
        configfilename = "configprod.json"
    
    path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    configfilepath = os.path.join(path, configfilename)
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
    
    config['twitter'] = {}
    
    for key in secret_dict.keys():
        secret_dict[key] = secret_dict[key] + suffix
        config['twitter'][key] = os.environ.get(secret_dict[key])

    return config

if __name__ == "__main__":
    getConfig()