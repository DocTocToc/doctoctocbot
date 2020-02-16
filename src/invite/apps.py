from django.apps import AppConfig


class InviteConfig(AppConfig):
    name = 'invite'

    def ready(self):
        import invite.signals #noqa