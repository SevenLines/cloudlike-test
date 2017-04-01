from django.contrib.auth.models import User
from django.test import TestCase

# Create your tests here.
from django.urls.base import reverse
from rest_framework.test import APIRequestFactory, APIClient


class LoggedSession(object):
    def __init__(self, client, username, password):
        self.client = client
        self.username = username
        self.password = password

    def __enter__(self):
        return self.client.login(username=self.username, password=self.password)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.logout()


class BaseTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user1 = User.objects.create_user(username="user1", password='123')
        self.user2 = User.objects.create_user(username="user2", password='123')

    def login(self, username='user1', password='123'):
        return LoggedSession(self.client, username, password)


class TestIndexPage(BaseTestCase):
    def test_index_redirect_to_login(self):
        r = self.client.get(reverse('index'))
        self.assertEqual(302, r.status_code)
        self.assertTrue(r.url.startswith(reverse("login")))

    def test_index_show_page_for_logged(self):
        with self.login():
            r = self.client.get(reverse('index'))
            self.assertEqual(200, r.status_code)
