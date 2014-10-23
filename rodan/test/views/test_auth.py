from rest_framework.test import APITestCase
from rest_framework import status
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin


class AuthViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()

    def test_authorized(self):
        can_log_in = self.client.login(username="ahankins", password="hahaha")
        self.assertTrue(can_log_in)

    def test_unauthorized(self):
        cant_log_in = self.client.login(username="foo", password="bar")
        self.assertFalse(cant_log_in)

    def test_session_status(self):
        response = self.client.get("/auth/status/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # log in and check again
        self.client.login(username="ahankins", password="hahaha")
        response = self.client.get("/auth/status/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_session_auth_pass(self):
        response = self.client.get("/")
        response = self.client.post("/auth/session/", {"username": "ahankins", "password": "hahaha"}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_session_auth_fail(self):
        response = self.client.get("/")
        response = self.client.post("/auth/session/", {"username": "ahankins", "password": "notgood"}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_token_auth_pass(self):
        token = self.client.post("/auth/token/", {"username": "ahankins", "password": "hahaha"}, format="multipart")
        response = self.client.get("/projects/", HTTP_AUTHORIZATION="Token {0}".format(token.data['token']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_auth_fail(self):
        token = self.client.post("/auth/token/", {"username": "ahankins", "password": "wrongg"}, format="multipart")
        self.assertEqual(token.data['non_field_errors'][0], "Unable to log in with provided credentials.")

    def tearDown(self):
        pass
