from rest_framework.test import APITestCase
from rest_framework import status
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
from rodan.models import InputPortType


class InputPortTypeViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_basic_workflow()
        self.client.login(username="ahankins", password="hahaha")

    def test_get_list(self):
        response = self.client.get("/inputporttypes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_detail(self):
        ipt = InputPortType.objects.first()
        response = self.client.get("/inputporttype/{0}/".format(ipt.uuid.hex))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['uuid'], ipt.uuid.hex)

    def test_post_not_allowed(self):
        ipt_obj = {
            'job': "http://localhost:8000/job/{0}/".format(self.test_job.uuid),
            'resource_types': ["http://localhost:8000/resourcetype/test/a1/", "http://localhost:8000/resourcetype/test/a2/"],
            'name': 'test',
            'minimum': 1,
            'maximum': 1
        }
        response = self.client.post("/inputporttypes/", ipt_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
