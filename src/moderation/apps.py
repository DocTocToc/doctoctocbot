from django.apps import AppConfig

class ModerationConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'moderation'
    
    def ready(self):
        import moderation.signals #noqa
    
