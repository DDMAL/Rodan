from rest_framework.test import APITestCase
from rest_framework import status
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
from rodan.models import ResourceType


class ResourceTypeViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_basic_workflow()
        self.client.force_authenticate(user=self.test_user)

    def test_get_list(self):
        response = self.client.get("/resourcetypes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_detail(self):
        rt = ResourceType.objects.first()
        response = self.client.get("/resourcetype/{0}/".format(rt.uuid.hex))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['uuid'], rt.uuid.hex)

    def test_post_not_allowed(self):
        rt_obj = {
            'mimetype': 'text/html',
        }
        response = self.client.post("/resourcetypes/", rt_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
