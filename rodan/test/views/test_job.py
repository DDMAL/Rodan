from rest_framework.test import APITestCase
from rest_framework import status
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
from rodan.models import Job
import uuid

class JobViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_basic_workflow()
        self.client.force_authenticate(user=self.test_user)

    def test_get_list(self):
        response = self.client.get("/jobs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_detail(self):
        job = Job.objects.first()
        response = self.client.get("/job/{0}/".format(job.uuid))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(uuid.UUID(response.data['uuid']), job.uuid)

    def test_post_not_allowed(self):
        job_obj = {
            'name': 'hahaha'
        }
        response = self.client.post("/jobs/", job_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
