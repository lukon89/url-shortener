import re

import requests
from django.test import LiveServerTestCase

from .db import urls_storage

SHORT_URL_PATTERN = re.compile(r"https?://.+/shrt/[a-zA-Z0-9]{6}$")


class ShortUrlCreateE2ETest(LiveServerTestCase):

    def setUp(self):
        urls_storage.clear()

    def tearDown(self):
        urls_storage.clear()

    def test_valid_url_returns_200(self):
        response = requests.post(f"{self.live_server_url}/api/shrt/", json={"url": "https://example.com"})
        self.assertEqual(response.status_code, 200)

    def test_response_short_url_matches_format(self):
        response = requests.post(f"{self.live_server_url}/api/shrt/", json={"url": "https://example.com"})
        self.assertRegex(response.json()["short_url"], SHORT_URL_PATTERN)

    def test_invalid_url_returns_400(self):
        response = requests.post(f"{self.live_server_url}/api/shrt/", json={"url": "not-a-url"})
        self.assertEqual(response.status_code, 400)

    def test_missing_field_returns_400(self):
        response = requests.post(f"{self.live_server_url}/api/shrt/", json={})
        self.assertEqual(response.status_code, 400)


class ShortUrlResolveE2ETest(LiveServerTestCase):

    def setUp(self):
        urls_storage.clear()

    def tearDown(self):
        urls_storage.clear()

    def test_nonexistent_code_returns_404(self):
        response = requests.get(f"{self.live_server_url}/api/shrt/doesnotexist/")
        self.assertEqual(response.status_code, 404)


class ShortUrlFlowE2ETest(LiveServerTestCase):

    def setUp(self):
        urls_storage.clear()

    def tearDown(self):
        urls_storage.clear()

    def _extract_code(self, short_url: str) -> str:
        return short_url.rstrip("/").split("/")[-1]

    def test_shorten_then_resolve_returns_original_url(self):
        long_url = "https://example.com/very/long/url"

        post_response = requests.post(f"{self.live_server_url}/api/shrt/", json={"url": long_url})
        self.assertEqual(post_response.status_code, 200)

        code = self._extract_code(post_response.json()["short_url"])
        get_response = requests.get(f"{self.live_server_url}/api/shrt/{code}/")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["long_url"], long_url)

    def test_multiple_urls_resolve_independently(self):
        urls = [
            "https://example.com/first",
            "https://example.com/second",
            "https://example.com/third",
        ]
        codes = []
        for url in urls:
            response = requests.post(f"{self.live_server_url}/api/shrt/", json={"url": url})
            self.assertEqual(response.status_code, 200)
            codes.append(self._extract_code(response.json()["short_url"]))

        self.assertEqual(len(set(codes)), len(urls))

        for code, expected_url in zip(codes, urls):
            response = requests.get(f"{self.live_server_url}/api/shrt/{code}/")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["long_url"], expected_url)
