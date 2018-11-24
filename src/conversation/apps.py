from django.apps import AppConfig


class ConversationConfig(AppConfig):
    name = 'conversation'

    def ready(self):
        import conversation.signals