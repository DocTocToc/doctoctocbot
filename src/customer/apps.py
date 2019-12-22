from django.apps import AppConfig


class CustomerConfig(AppConfig):
    name = 'customer'

    def ready(self):
        import customer.signals  # noqa