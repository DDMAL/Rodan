from rest_framework.test import APITestCase
from rest_framework import status
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin


class AuthViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()

    def test_token_auth_pass(self):
        token = self.client.post("/auth/token/", {"username": "ahankins", "password": "hahaha"}, format="multipart")
        token_header = "Token {0}".format(token.data['token'])

        response = self.client.get("/projects/", HTTP_AUTHORIZATION=token_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get("/auth/me/", HTTP_AUTHORIZATION=token_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_auth_fail(self):
        token = self.client.post("/auth/token/", {"username": "ahankins", "password": "wrongg"}, format="multipart")
        self.assertEqual(token.data, {'is_logged_in': False})

        response = self.client.get("/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
