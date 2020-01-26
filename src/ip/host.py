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

def ip_yours(request):
    logger.debug(request.META)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        logger.debug(f'HTTP_X_FORWARDED_FOR: {x_forwarded_for}')
        ip = x_forwarded_for.split(',')[0].strip()
    elif request.META.get('HTTP_X_REAL_IP'):
        ip = request.META.get('HTTP_X_REAL_IP')
        logger.debug(f'HTTP_X_REAL_IP: {ip}')
    else:
        ip = request.META.get('REMOTE_ADDR')
        logger.debug(f'REMOTE_ADDR: {ip}')
    return ip

def set_discourse_ip_cache():
    discourse_ip = hostname_ip(settings.DISCOURSE_HOSTNAME)
    cache.set(settings.DISCOURSE_IP_CACHE_KEY, discourse_ip, settings.DISCOURSE_IP_CACHE_TTL)
    return discourse_ip