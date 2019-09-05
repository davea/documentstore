from django.test import TestCase
from django.urls import reverse


class DropboxHookTests(TestCase):
    def test_invalid_methods(self):
        for method in [
            self.client.put,
            self.client.head,
            self.client.trace,
            self.client.options,
            self.client.delete,
            self.client.patch,
        ]:
            self.assertEqual(method(reverse("hooks:dropbox")).status_code, 405)

    def test_invalid_user_agent(self):
        response = self.client.get(reverse("hooks:dropbox"), HTTP_USER_AGENT="curl/1.0")
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            reverse("hooks:dropbox"), HTTP_USER_AGENT="curl/1.0"
        )
        self.assertEqual(response.status_code, 400)

    def test_challenge_response(self):
        response = self.client.get(
            reverse("hooks:dropbox"),
            {"challenge": "mySuperCoolChallenge"},
            HTTP_USER_AGENT="DropboxWebhooks/1.0",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"mySuperCoolChallenge")
