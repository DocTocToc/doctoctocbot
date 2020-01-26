import socket
import logging
from django.http import HttpResponse

logger= logging.getLogger(__name__)

def ip_mine(request):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)                        
    s.connect(("8.8.4.4", 80))                                                  
    MACHINE_IP = s.getsockname()[0]                                             
    s.close()                                                                   
    return HttpResponse(MACHINE_IP)

def ip_yours(request):
    logger.debug(request.META)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if request.META.get('HTTP_X_REAL_IP'):
        ip = request.META.get('HTTP_X_REAL_IP')
        logger.debug(f'HTTP_X_REAL_IP: {ip}')
    elif x_forwarded_for:
        logger.debug(f'HTTP_X_FORWARDED_FOR: {x_forwarded_for}')
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
        logger.debug(f'REMOTE_ADDR: {ip}')
    return HttpResponse(ip)