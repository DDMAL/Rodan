from rest_framework.test import APITestCase
from rest_framework import status
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
from rodan.models import OutputPortType
import uuid


class OutputPortTypeViewTestCase(
    RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin
):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_basic_workflow()
        self.client.force_authenticate(user=self.test_user)

    def test_get_list(self):
        response = self.client.get("/api/outputporttypes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("current_page", response.data)

        # test disable pagination
        response = self.client.get("/api/outputporttypes/?disable_pagination=yes")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("results", response.data)
        self.assertNotIn("current_page", response.data)
        self.assertEqual(len(response.data), OutputPortType.objects.all().count())

    def test_get_detail(self):
        opt = OutputPortType.objects.first()
        response = self.client.get("/api/outputporttype/{0}/".format(opt.uuid))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(uuid.UUID(response.data["uuid"]), opt.uuid)

    def test_post_not_allowed(self):
        opt_obj = {
            "job": "http://localhost:8000/api/job/{0}/".format(self.test_job.uuid),
            "resource_types": ["http://localhost:8000/api/resourcetype/test/a1/"],
            "name": "test",
            "minimum": 1,
            "maximum": 1,
        }

        response = self.client.post("/api/outputporttypes/", opt_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
