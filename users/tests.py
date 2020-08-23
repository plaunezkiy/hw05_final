from django.test import TestCase, Client
from django.urls import reverse


class TestUsersApp(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup(self):
        username = "test_username"
        self.client.post(reverse("signup"),
                         {"first_name": "Test",
                          "last_name": "Testov",
                          "username": username,
                          "email": "test@test.test",
                          "password1": "Test123$",
                          "password2": "Test123$"},
                         follow=True)

        response = self.client.get(reverse("profile", args=(username,)))
        self.assertEqual(response.status_code, 200)
