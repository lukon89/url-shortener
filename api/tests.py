from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase

class HelloViewTest(APITestCase):

    def test_get_returns_200(self):
        response = self.client.get('/api/hello/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "Hello!")
