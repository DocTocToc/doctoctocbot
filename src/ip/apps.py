from django.apps import AppConfig
from ip.host import set_discourse_ip_cache


class IpConfig(AppConfig):
    name = 'ip'

    def ready(self):
        set_discourse_ip_cache