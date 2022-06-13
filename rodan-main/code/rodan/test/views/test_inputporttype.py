from rest_framework.test import APITestCase
from rest_framework import status
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
from rodan.models import InputPortType
import uuid


class InputPortTypeViewTestCase(
    RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin
):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_basic_workflow()
        self.client.force_authenticate(user=self.test_user)

    def test_get_list(self):
        response = self.client.get("/api/inputporttypes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("current_page", response.data)

        # test disable pagination
        response = self.client.get("/api/inputporttypes/?disable_pagination=yes")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("results", response.data)
        self.assertNotIn("current_page", response.data)
        self.assertEqual(len(response.data), InputPortType.objects.all().count())

    def test_get_detail(self):
        ipt = InputPortType.objects.first()
        response = self.client.get("/api/inputporttype/{0}/".format(ipt.uuid))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(uuid.UUID(response.data["uuid"]), ipt.uuid)

    def test_post_not_allowed(self):
        ipt_obj = {
            "job": "http://localhost:8000/api/job/{0}/".format(self.test_job.uuid),
            "resource_types": [
                "http://localhost:8000/api/resourcetype/test/a1/",
                "http://localhost:8000/api/resourcetype/test/a2/",
            ],
            "name": "test",
            "minimum": 1,
            "maximum": 1,
        }
        response = self.client.post("/api/inputporttypes/", ipt_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
