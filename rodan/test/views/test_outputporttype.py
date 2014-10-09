from rodan.models.resource import ResourceType
from rest_framework.test import APITestCase
from rest_framework import status
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin

FLOAT = ResourceType.FLOAT


class OutputPortTypeViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_basic_workflow()
        self.client.login(username="ahankins", password="hahaha")

    def test_post(self):
        opt_obj = {
            'job': "http://localhost:8000/job/{0}/".format(self.test_job.uuid),
            'resource_type': [FLOAT],
            'name': 'test',
            'minimum': 1,
            'maximum': 1
        }

        response = self.client.post("/outputporttypes/", opt_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_no_min_max(self):
        opt_obj = {
            'job': "http://localhost:8000/job/{0}/".format(self.test_job.uuid),
            'resource_type': [FLOAT],
            'name': 'test'
        }

        response = self.client.post("/outputporttypes/", opt_obj, format='json')
        anticipated_message = {'maximum': ['This field is required.'],
                               'minimum': ['This field is required.']}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_no_name(self):
        opt_obj = {
            'job': "http://localhost:8000/job/{0}/".format(self.test_job.uuid),
            'resource_type': [FLOAT],
            'minimum': 1,
            'maximum': 1
        }

        response = self.client.post("/outputporttypes/", opt_obj, format='json')
        anticipated_message = {'name': ['This field is required.']}

        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
