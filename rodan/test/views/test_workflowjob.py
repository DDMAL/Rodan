from rest_framework.test import APITestCase
from rest_framework import status
from rodan.models import Job, WorkflowJob
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
from model_mommy import mommy


class WorkflowJobViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.test_job = mommy.make('rodan.Job',
                                   settings={
                                       'type': 'object',
                                       'required': ['a'],
                                       'properties': {
                                           'a': {
                                               'type': 'number',
                                               'default': 6.5
                                           },
                                           'b': {
                                               'type': 'number'
                                           }
                                       }
                                   })
        self.test_workflow = mommy.make('rodan.Workflow')
        self.client.login(username="ahankins", password="hahaha")
    def test_create_default_settings(self):
        wfj_obj = {
            'workflow': "http://localhost:8000/workflow/{0}/".format(self.test_workflow.uuid),
            'job': 'http://localhost:8000/job/{0}/'.format(self.test_job.uuid)
        }
        response = self.client.post("/workflowjobs/", wfj_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['job_settings'], {'a': 6.5})

    def test_create_provide_settings(self):
        wfj_obj = {
            'workflow': "http://localhost:8000/workflow/{0}/".format(self.test_workflow.uuid),
            'job': 'http://localhost:8000/job/{0}/'.format(self.test_job.uuid),
            'job_settings': {}
        }
        response = self.client.post("/workflowjobs/", wfj_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['job_settings'], {})
