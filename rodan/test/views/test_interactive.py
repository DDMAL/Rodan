import uuid, json
from rest_framework.test import APITestCase
from rest_framework import status
from model_mommy import mommy
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
from rodan.models import Resource, Job, ResourceType
from rodan.constants import task_status
from django.core.files.base import ContentFile

class InteractiveTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.client.login(username='ahankins', password='hahaha')

        dummy_m_job = Job.objects.get(job_name='rodan.jobs.devel.dummy_manual_job')
        self.test_project = mommy.make('rodan.Project')
        self.test_workflow = mommy.make('rodan.Workflow', project=self.test_project)
        self.test_resource_in = mommy.make('rodan.Resource',
                                           project=self.test_project,
                                           compat_resource_file="dummy",
                                           resource_type=ResourceType.cached('test/a1'))
        self.test_resource_out = mommy.make('rodan.Resource',
                                            project=self.test_project,
                                            compat_resource_file="",
                                            resource_type=ResourceType.cached('test/a1'))
        self.test_runjob = mommy.make('rodan.RunJob',
                                      job_name=dummy_m_job.job_name,
                                      status=task_status.WAITING_FOR_INPUT,
                                      workflow_run__status=task_status.PROCESSING,
                                      workflow_run__workflow=self.test_workflow)
        input_m = mommy.make('rodan.Input',
                             run_job=self.test_runjob,
                             input_port_type_name='in_typeA',
                             resource=self.test_resource_in)
        output_m = mommy.make('rodan.Output',
                              run_job=self.test_runjob,
                              output_port_type_name='out_typeA',
                              resource=self.test_resource_out)
        self.test_resource_out.origin = output_m
        self.test_resource_out.save()
        self.test_resource_in.compat_resource_file.save('dummy.txt', ContentFile('{"test": "hahaha"}'))

    def test_not_exist(self):
        response = self.client.get("/interactive/{0}/".format(uuid.uuid1().hex), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.post("/interactive/{0}/".format(uuid.uuid1().hex), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_not_waiting_for_input(self):
        self.test_runjob.status = task_status.SCHEDULED
        self.test_runjob.save()
        response = self.client.get("/interactive/{0}/".format(self.test_runjob.uuid), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'message': 'This RunJob does not accept input now'})
        response = self.client.post("/interactive/{0}/".format(self.test_runjob.uuid), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'message': 'This RunJob does not accept input now'})

    def test_get__success(self):
        response = self.client.get("/interactive/{0}/".format(self.test_runjob.uuid))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, "dummy hahaha")
    def test_post__fail(self):
        response = self.client.post("/interactive/{0}/".format(self.test_runjob.uuid), {'fail': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'detail': 'dummy manual job error'})
    def test_post__success(self):
        response = self.client.post("/interactive/{0}/".format(self.test_runjob.uuid), [1,2,3,4], format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        path = Resource.objects.get(uuid=self.test_resource_out.uuid).compat_resource_file.path
        with open(path) as f:
            self.assertEqual(json.load(f), [1, 2, 3, 4])
