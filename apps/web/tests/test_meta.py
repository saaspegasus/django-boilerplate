from django.contrib.sites.models import Site
from django.test import TestCase

from apps.web.meta import absolute_url, get_protocol, get_server_root


class MetaUrlTest(TestCase):
    def setUp(self):
        site = Site.objects.get_current()
        site.domain = "example.com"
        site.save()
        Site.objects.clear_cache()

    def tearDown(self):
        Site.objects.clear_cache()

    def test_get_protocol(self):
        self.assertEqual(get_protocol(is_secure=False), "http")
        self.assertEqual(get_protocol(is_secure=True), "https")

    def test_get_server_root(self):
        self.assertEqual(get_server_root(is_secure=True), "https://example.com")
        self.assertEqual(get_server_root(is_secure=False), "http://example.com")

    def test_absolute_url(self):
        self.assertEqual(absolute_url("/dashboard/", is_secure=True), "https://example.com/dashboard/")
        self.assertEqual(absolute_url("/dashboard/", is_secure=False), "http://example.com/dashboard/")
