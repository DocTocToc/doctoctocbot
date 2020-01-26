import socket
from django.http import HttpResponse

def ip_mine(request):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)                        
    s.connect(("8.8.4.4", 80))                                                  
    MACHINE_IP = s.getsockname()[0]                                             
    s.close()                                                                   
    return HttpResponse(MACHINE_IP)

def ip_yours(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    elif request.META.get('HTTP_X_REAL_IP'):
        ip = request.META.get('HTTP_X_REAL_IP')
    else:
        ip = request.META.get('REMOTE_ADDR')
    return HttpResponse(ip)