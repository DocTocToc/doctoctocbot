from django.apps import AppConfig

class ModerationConfig(AppConfig):
    name = 'moderation'
    
    def ready(self):
        import moderation.signals #noqa
    
