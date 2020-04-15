from rest_framework.test import APITestCase
from rest_framework import status
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
from rodan.models import ResourceType
import uuid


class ResourceTypeViewTestCase(
    RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin
):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_basic_workflow()
        self.client.force_authenticate(user=self.test_user)

    def test_get_list(self):
        response = self.client.get("/api/resourcetypes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("current_page", response.data)

        # test disable pagination
        response = self.client.get("/api/resourcetypes/?disable_pagination=yes")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("results", response.data)
        self.assertNotIn("current_page", response.data)
        self.assertEqual(len(response.data), ResourceType.objects.all().count())

    def test_get_detail(self):
        rt = ResourceType.objects.first()
        response = self.client.get("/api/resourcetype/{0}/".format(rt.uuid))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(uuid.UUID(response.data["uuid"]), rt.uuid)

    def test_post_not_allowed(self):
        rt_obj = {"mimetype": "text/html"}
        response = self.client.post("/api/resourcetypes/", rt_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
