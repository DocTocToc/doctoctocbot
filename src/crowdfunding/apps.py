from django.apps import AppConfig


class CrowdfundingConfig(AppConfig):
    name = 'crowdfunding'

    def ready(self):
        import crowdfunding.signals  # noqa