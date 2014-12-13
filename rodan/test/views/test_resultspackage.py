import os, json, zipfile
from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

from rodan.models import WorkflowRun, Workflow, WorkflowJob, InputPort, InputPortType, OutputPort, OutputPortType, Connection, Job, RunJob, ResourceType, ResultsPackage
from model_mommy import mommy
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
import uuid
from django.core.files.base import ContentFile
from rodan.models.resource import upload_path
from rodan.constants import task_status

class ResultsPackageSimpleTest(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_simple_dummy_workflow()
        self.client.login(username="ahankins", password="hahaha")

        # Run this dummy workflow
        self.test_resource_content = 'dummy text'
        self.test_resource.compat_resource_file.save('dummy.txt', ContentFile(self.test_resource_content))
        response = self.client.patch("/workflow/{0}/".format(self.test_workflow.uuid), {'valid': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/{0}/'.format(self.test_user.pk),
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid)
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wfrun_id = response.data['uuid']
        dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()

        self.test_user_input = {'foo': 'bar'}
        response = self.client.post("/interactive/{0}/".format(str(dummy_m_runjob.uuid)), self.test_user_input)

        self.test_workflowrun = WorkflowRun.objects.get(uuid=wfrun_id)
        self.assertEqual(self.test_workflowrun.status, task_status.FINISHED)

        self.output_a = self.dummy_a_wfjob.run_jobs.first().outputs.first()
        self.output_m = self.dummy_m_wfjob.run_jobs.first().outputs.first()

    def test_all_ports(self):
        resultspackage_obj = {
            'workflow_run': 'http://localhost:8000/workflowrun/{0}/'.format(self.test_workflowrun.uuid),
            'output_ports': ['http://localhost:8000/outputport/{0}/'.format(self.output_a.output_port.uuid),
                             'http://localhost:8000/outputport/{0}/'.format(self.output_m.output_port.uuid)
            ]
        }
        response = self.client.post("/resultspackages/", resultspackage_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        rp_id = response.data['uuid']
        rp = ResultsPackage.objects.get(uuid=rp_id)
        #print rp.error_summary, rp.error_details
        self.assertEqual(rp.status, task_status.FINISHED)
        self.assertEqual(rp.percent_completed, 100)

        with zipfile.ZipFile(rp.package_path, 'r') as z:
            files = z.namelist()
            # TODO: test file names
