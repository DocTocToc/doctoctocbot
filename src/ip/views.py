import socket
import logging
from django.http import HttpResponse
from ip.host import ip_yours

logger= logging.getLogger(__name__)

def mine(request):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)                        
    s.connect(("8.8.4.4", 80))                                                  
    MACHINE_IP = s.getsockname()[0]                                             
    s.close()                                                                   
    return HttpResponse(MACHINE_IP)

def yours(request):
    return HttpResponse(ip_yours(request))