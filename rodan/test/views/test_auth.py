from rest_framework.test import APITestCase
from rest_framework import status
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
from rest_framework.reverse import reverse


class AuthViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()

    def test_token_auth_pass(self):
        token = self.client.post(
            "/auth/token/",
            {"username": "ahankins", "password": "hahaha"},
            format="multipart",
        )
        token_header = "Token {0}".format(token.data["token"])

        response = self.client.get("/projects/", HTTP_AUTHORIZATION=token_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get("/auth/me/", HTTP_AUTHORIZATION=token_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_auth_fail(self):
        token = self.client.post(
            "/auth/token/",
            {"username": "ahankins", "password": "wrongg"},
            format="multipart",
        )
        self.assertEqual(token.data, {"is_logged_in": False})

        response = self.client.get("/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_me(self):
        self.client.force_authenticate(user=self.test_user)
        response = self.client.get(reverse("auth-me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.test_user.username)

        # Create a project and test groups
        proj_obj = {
            "creator": "http://localhost:8000/user/{0}/".format(self.test_user.pk),
            "description": "Created Project",
            "name": "Another Test Project",
        }
        response = self.client.post("/projects/", proj_obj, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        response = self.client.get(reverse("auth-me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_other_auth_views(self):
        "Only to verify that they don't throw 500 due to an update of djoser library."
        self.client.force_authenticate(user=self.test_user)
        for v in ["auth-register", "auth-reset-token", "auth-change-password"]:
            response = self.client.get(reverse(v))
            self.assertNotEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )
