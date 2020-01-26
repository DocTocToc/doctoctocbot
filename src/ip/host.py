import socket 
import logging
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

def hostname_ip(hostname):
    try: 
        host_ip = socket.gethostbyname(hostname) 
        logger.debug(f"Hostname : {hostname}, IP: {host_ip}") 
        return host_ip 
    except:
        logger.debug(f"Unable to get IP for {hostname}")
        return None
    
def set_discourse_ip_cache():
    discourse_ip = hostname_ip(settings.DISCOURSE_HOSTNAME)
    cache.set(settings.DISCOURSE_IP_CACHE_KEY, discourse_ip, settings.DISCOURSE_IP_CACHE_TTL)
    return discourse_ip