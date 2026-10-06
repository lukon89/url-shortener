import re

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from api.db import urls_storage

SHORT_URL_PATTERN = re.compile(r"https?://.+/shrt/[a-zA-Z0-9]{6}$")


@override_settings(ALLOWED_HOSTS=["example.com"])
class ShortUrlCreateViewTest(APITestCase):

    def setUp(self):
        urls_storage.clear()
        self.client.defaults["SERVER_NAME"] = "example.com"

    def tearDown(self):
        urls_storage.clear()

    def test_valid_url_returns_200(self):
        response = self.client.post("/api/shrt/", {"url": "https://example.com/very/long/url"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertRegex(response.data["short_url"], SHORT_URL_PATTERN)

    def test_valid_url_short(self):
        response = self.client.post("/api/shrt/", {"url": "https://www.google.pl/a"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertRegex(response.data["short_url"], SHORT_URL_PATTERN)

    def test_valid_url_no_path(self):
        response = self.client.post("/api/shrt/", {"url": "https://example.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertRegex(response.data["short_url"], SHORT_URL_PATTERN)

    def test_valid_url_with_query_params(self):
        response = self.client.post("/api/shrt/", {"url": "https://example.com/path?param=value&other=123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertRegex(response.data["short_url"], SHORT_URL_PATTERN)

    def test_invalid_url_not_a_url(self):
        response = self.client.post("/api/shrt/", {"url": "not-a-url"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_url_only_scheme(self):
        response = self.client.post("/api/shrt/", {"url": "http://"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_url_empty_string(self):
        response = self.client.post("/api/shrt/", {"url": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_url_missing_field(self):
        response = self.client.post("/api/shrt/", {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_response_contains_short_url_in_correct_format(self):
        response = self.client.post("/api/shrt/", {"url": "https://example.com"})
        self.assertIn("short_url", response.data)
        self.assertRegex(response.data["short_url"], SHORT_URL_PATTERN)


@override_settings(ALLOWED_HOSTS=["example.com"])
class ShortUrlFlowTest(APITestCase):

    def setUp(self):
        urls_storage.clear()
        self.client.defaults["SERVER_NAME"] = "example.com"

    def tearDown(self):
        urls_storage.clear()

    def _extract_code(self, short_url: str) -> str:
        return short_url.rstrip("/").split("/")[-1]

    def test_shorten_then_resolve_returns_original_url(self):
        long_url = "https://example.com/very/long/url"
        post_response = self.client.post("/api/shrt/", {"url": long_url})
        self.assertEqual(post_response.status_code, status.HTTP_200_OK)

        code = self._extract_code(post_response.data["short_url"])
        get_response = self.client.get(f"/api/shrt/{code}/")
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data["long_url"], long_url)

    def test_multiple_urls_resolve_independently(self):
        urls = [
            "https://example.com/first",
            "https://example.com/second",
            "https://example.com/third",
        ]
        codes = []
        for url in urls:
            response = self.client.post("/api/shrt/", {"url": url})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            codes.append(self._extract_code(response.data["short_url"]))

        self.assertEqual(len(set(codes)), len(urls))

        for code, expected_url in zip(codes, urls):
            response = self.client.get(f"/api/shrt/{code}/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["long_url"], expected_url)


class ShortUrlResolveViewTest(APITestCase):

    def setUp(self):
        urls_storage.clear()
        urls_storage["abc123"] = "https://example.com/original"

    def tearDown(self):
        urls_storage.clear()

    def test_existing_code_returns_200(self):
        response = self.client.get("/api/shrt/abc123/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_nonexistent_code_returns_404(self):
        response = self.client.get("/api/shrt/doesnotexist/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_response_contains_long_url(self):
        response = self.client.get("/api/shrt/abc123/")
        self.assertIn("long_url", response.data)

    def test_long_url_matches_stored_value(self):
        response = self.client.get("/api/shrt/abc123/")
        self.assertEqual(response.data["long_url"], "https://example.com/original")
