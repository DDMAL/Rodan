from rest_framework.test import APITestCase
from rest_framework import status
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
from rodan.models import Job


class JobViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_basic_workflow()
        self.client.login(username="ahankins", password="hahaha")

    def test_get_list(self):
        response = self.client.get("/jobs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_detail(self):
        job = Job.objects.first()
        response = self.client.get("/job/{0}/".format(job.uuid.hex))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['uuid'], job.uuid.hex)

    def test_post_not_allowed(self):
        job_obj = {
            'job_name': 'hahaha'
        }
        response = self.client.post("/jobs/", job_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
