import socket 
import logging

logger = logging.getLogger(__name__)

def hostname_ip(hostname):
    try: 
        host_ip = socket.gethostbyname(hostname) 
        logger.debug(f"Hostname : {hostname}, IP: {host_ip}") 
        return(host_ip) 
    except:
        logger.debug(f"Unable to get IP for {hostname}")
        return None