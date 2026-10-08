from unittest import mock

from django import forms
from django.test import SimpleTestCase, override_settings

from apps.users.forms import TurnstileSignupForm


@override_settings(TURNSTILE_SECRET="test-secret")
class TurnstileSignupFormTest(SimpleTestCase):
    def _clean_token(self, siteverify_response: dict):
        form = TurnstileSignupForm()
        form.cleaned_data = {"turnstile_token": "test-token"}
        with mock.patch("apps.users.forms.requests.post") as mock_post:
            mock_post.return_value.json.return_value = siteverify_response
            return form.clean_turnstile_token()

    @override_settings(DEBUG=False)
    def test_valid_token(self):
        self.assertEqual("test-token", self._clean_token({"success": True, "hostname": "example.com"}))

    @override_settings(DEBUG=False)
    def test_unsuccessful_token_rejected(self):
        with self.assertRaises(forms.ValidationError):
            self._clean_token({"success": False})

    @override_settings(DEBUG=False)
    def test_local_hostname_rejected_in_production(self):
        for hostname in ["localhost", "127.0.0.1"]:
            with self.subTest(hostname=hostname), self.assertRaises(forms.ValidationError):
                self._clean_token({"success": True, "hostname": hostname})

    @override_settings(DEBUG=True)
    def test_local_hostname_allowed_in_debug(self):
        self.assertEqual("test-token", self._clean_token({"success": True, "hostname": "localhost"}))
