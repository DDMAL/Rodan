from rest_framework.test import APITestCase
from rest_framework import status
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin


class UserPreferenceViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_basic_workflow()
        self.client.force_authenticate(user=self.test_superuser)

    def test_post(self):
        up_obj = {
            "user": "http://localhost:8000/user/{0}/".format(self.test_user.id),
            "send_email": "false"
        }

        response = self.client.post("/userpreferences/", up_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

