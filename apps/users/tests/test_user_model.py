from allauth.account.models import EmailAddress
from django.test import SimpleTestCase, TestCase

from apps.users.models import CustomUser


class DisplayNameTest(SimpleTestCase):
    def test_uses_full_name_when_set(self):
        user = CustomUser(first_name="Ada", last_name="Lovelace", email="ada@example.com")
        self.assertEqual(user.get_display_name(), "Ada Lovelace")

    def test_falls_back_to_email(self):
        user = CustomUser(email="ada@example.com", username="ada-username")
        self.assertEqual(user.get_display_name(), "ada@example.com")

    def test_falls_back_to_username_without_email(self):
        user = CustomUser(username="ada-username")
        self.assertEqual(user.get_display_name(), "ada-username")

    def test_str_includes_name_and_email(self):
        user = CustomUser(first_name="Ada", last_name="Lovelace", email="ada@example.com")
        self.assertEqual(str(user), "Ada Lovelace <ada@example.com>")


class GravatarTest(SimpleTestCase):
    def test_gravatar_id_is_md5_of_email(self):
        user = CustomUser(email="test@example.com")
        self.assertEqual(user.gravatar_id, "55502f40dc8b7c769880b10874abc9d0")

    def test_gravatar_id_normalizes_case_and_whitespace(self):
        self.assertEqual(
            CustomUser(email=" TEST@Example.com ").gravatar_id,
            CustomUser(email="test@example.com").gravatar_id,
        )

    def test_avatar_url_falls_back_to_gravatar(self):
        user = CustomUser(email="test@example.com")
        self.assertEqual(
            user.avatar_url,
            "https://www.gravatar.com/avatar/55502f40dc8b7c769880b10874abc9d0?s=128&d=identicon",
        )


class HasVerifiedEmailTest(TestCase):
    def test_verified_email(self):
        user = CustomUser.objects.create(username="a@example.com", email="a@example.com")
        EmailAddress.objects.create(user=user, email="a@example.com", verified=True, primary=True)
        self.assertTrue(user.has_verified_email)

    def test_unverified_email(self):
        user = CustomUser.objects.create(username="b@example.com", email="b@example.com")
        EmailAddress.objects.create(user=user, email="b@example.com", verified=False, primary=True)
        self.assertFalse(user.has_verified_email)

    def test_no_email_records(self):
        user = CustomUser.objects.create(username="c@example.com", email="c@example.com")
        self.assertFalse(user.has_verified_email)
