import os
import inspect
import json

def getConfig():                                                        
    """
    Get config object.
    To use production configuration file, export environement variable
    BOT_DEBUG=False. Without this environment variable, defaults to configtest.json.
    """
    DEBUG = bool(os.environ.get('BOT_DEBUG', True))
    if DEBUG:
        configfilename = "configtest.json"
    else:
        configfilename = "configprod.json"
    path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    configfilepath = os.path.join(path, configfilename)
    #config = configparser.SafeConfigParser()
    #config.read(configfilepath)
    config = json.load(open(configfilepath)) 
    return config
