from django.apps import AppConfig


class HiveConfig(AppConfig):
    name = 'hive'

    def ready(self):
        import hive.signals
        import conversation.signals