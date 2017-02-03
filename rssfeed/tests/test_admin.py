from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client


class AdminTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.editor = get_user_model().objects.create(
            username="test",
            email="test@test.com",
            is_superuser=True,
            is_staff=True
        )
        self.editor.set_password("password")
        self.editor.save()
        self.client.login(username="test", password="password")

    def test_admin(self):
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/admin/rssfeed/")
        self.assertEqual(response.status_code, 200)

    def test_admin_entry(self):
        response = self.client.get("/admin/rssfeed/entry/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/admin/rssfeed/entry/add/")
        self.assertEqual(response.status_code, 200)

    def test_admin_feed(self):
        response = self.client.get("/admin/rssfeed/feed/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/admin/rssfeed/feed/add/")
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        pass
