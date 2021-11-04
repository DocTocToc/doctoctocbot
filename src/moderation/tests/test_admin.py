import logging
import factory
from moderation.models import Queue, SocialUser

from users.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.db.models import signals

logger = logging.getLogger(__name__)

def get_admin_change_view_url(obj: object) -> str:
    return reverse(
        'admin:{}_{}_change'.format(
            obj._meta.app_label,
            type(obj).__name__.lower()
        ),
        args=(obj.pk,)
    )
    
def get_admin_list_view_url(obj: object) -> str:
    return reverse(
        'admin:{}_{}_changelist'.format(
            obj._meta.app_label,
            type(obj).__name__.lower()
        )
    )


class TestQueueAdmin(TestCase):
    def setUp(self):
        try:
            self.user = User.objects.get(username='test_admin_user')
            assert self.user.is_staff, "Error: test_admin_user is not staff"
            assert self.user.is_superuser, "Error: test_admin_user is not admin"
        except User.DoesNotExist:
            self.user = User.objects.create_user(
            username='test_admin_user',
            password='12345',
            is_superuser=True,
            is_staff=True
        )
        self.client.login(username='test_admin_user', password='12345')

    def test_change_view_loads_normally(self):
        # prepare client
        q = Queue()
        url = get_admin_change_view_url(q)
        logger.debug(url)
        response = self.client.get(url, follow=True)
        logger.debug(response)
        self.assertEqual(response.status_code, 200)

    def test_list_view_loads_normally(self):
        q = Queue()
        url = get_admin_list_view_url(q)
        logger.debug(url)
        response = self.client.get(url, follow=True)
        logger.debug(response)
        self.assertEqual(response.status_code, 200)

    
class SocialUserAdmin(TestCase):
    def setUp(self):
        try:
            self.user = User.objects.get(username='test_admin_user')
            assert self.user.is_staff, "Error: test_admin_user is not staff"
            assert self.user.is_superuser, "Error: test_admin_user is not admin"
        except User.DoesNotExist:
            self.user = User.objects.create_user(
            username='test_admin_user',
            password='12345',
            is_superuser=True,
            is_staff=True
        )
        self.client.login(username='test_admin_user', password='12345')

    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def test_change_view_loads_normally(self):
        # prepare client
        su = SocialUser()
        url = get_admin_change_view_url(su)
        logger.debug(url)
        response = self.client.get(url, follow=True)
        logger.debug(response)
        self.assertEqual(response.status_code, 200)

    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def test_list_view_loads_normally(self):
        su = SocialUser()
        url = get_admin_list_view_url(su)
        logger.debug(url)
        response = self.client.get(url, follow=True)
        logger.debug(response)
        self.assertEqual(response.status_code, 200)