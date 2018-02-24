import os
import inspect
import configparser

def getConfig():                                                        
    "get config object"                                               
    configfilename = "configtest"
    path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    configfilepath = os.path.join(path, configfilename)
    config = configparser.SafeConfigParser()
    config.read(configfilepath) 
    return config  

def getWhitelist():
    "get user whitelist"
    path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    #docs = getConfig().get("Settings", "white_list_file")
    docs = "docs"
    docsfile = os.path.join(path, docs)
    with open(docsfile, 'r') as f:
        whitelist = [int(line.rstrip('\n')) for line in f]
    return whitelist

whitelist = getWhitelist()

