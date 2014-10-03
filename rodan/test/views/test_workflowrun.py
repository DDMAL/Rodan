import os
from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

from rodan.models.workflowrun import WorkflowRun
from rodan.models.workflow import Workflow
from rodan.models.runjob import RunJobStatus
from rodan.models.workflowjob import WorkflowJob
from rodan.models.inputport import InputPort
from rodan.models.inputporttype import InputPortType
from rodan.models.outputport import OutputPort
from rodan.models.outputporttype import OutputPortType
from rodan.models.connection import Connection
from rodan.models.job import Job
from rodan.models.runjob import RunJob
from rodan.views.workflowrun import WorkflowRunList
from model_mommy import mommy
from rodan.test.RodanTestHelpers import RodanTestSetUpMixin, RodanTestTearDownMixin
import uuid


class WorkflowRunViewTest(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_basic_workflow()
        self.client.login(username="ahankins", password="hahaha")

    def test_post(self):
        workflow_update = {
            'valid': True,
        }
        self.client.patch("/workflow/{0}/".format(self.test_workflow.uuid), workflow_update, format='json')

        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/{0}/'.format(self.test_user.pk),
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
        }

        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_no_workflow_ID(self):
        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/{0}/'.format(self.test_user.pk),
            'workflow': None,
        }

        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {"message": "You must specify a workflow ID"}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_no_existing_workflow(self):
        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/{0}/'.format(self.test_user.pk),
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(uuid.uuid1()),
        }

        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {"message": "You must specify an existing workflow"}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_patch_not_found(self):
        workflowrun_update = {'run': 5}
        response = self.client.patch("/workflowrun/{0}/".format(uuid.uuid1()), workflowrun_update, format='json')
        anticipated_message = {'message': 'Workflow_run not found'}
        self.assertEqual(anticipated_message, response.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_already_cancelled(self):
        wfrun = mommy.make('rodan.WorkflowRun',
                           cancelled=True)
        workflowrun_update = {'cancelled': False}
        response = self.client.patch("/workflowrun/{0}/".format(wfrun.uuid), workflowrun_update, format='json')
        anticipated_message = {"message": "Workflowrun cannot be uncancelled."}
        self.assertEqual(anticipated_message, response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

"""
    def test_patch(self):
        workflowrun_update = {'run': WorkflowRun.objects.get(pk="eb4b3661be2a44908c4c932b0783bb3e").run+1}
        response = self.client.patch("/workflowrun/eb4b3661be2a44908c4c932b0783bb3e/", workflowrun_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_endpoint_workflow_jobs(self):
        endpoints = WorkflowRunList._endpoint_workflow_jobs(WorkflowRunList(), self.test_workflow)
        self.assertEqual(endpoints, [WorkflowJob.objects.get(uuid="a21f510a16c24701ac0e435b3f4c20f3")])

    def test_singleton_workflow_jobs(self):
        single_workflowjob = WorkflowJob(workflow=self.test_workflow, job=self.test_job)
        single_workflowjob.save()

        test_outputporttype = OutputPortType.objects.get(uuid="1cdb067e98194da48dd3dfa35e84671c")
        single_outputport = OutputPort(workflow_job=single_workflowjob, output_port_type=test_outputporttype)
        single_outputport.save()

        test_workflowjob2 = WorkflowJob.objects.get(uuid="a21f510a16c24701ac0e435b3f4c20f3")

        test_inputporttype = InputPortType.objects.get(uuid="30ed42546fe440a181f64a2ebdea82e1")
        test_second_inputport = InputPort(workflow_job=test_workflowjob2, input_port_type=test_inputporttype)
        test_second_inputport.save()

        connection2_data = {
            'input_port': test_second_inputport,
            'input_workflow_job': test_workflowjob2,
            'output_port': single_outputport,
            'output_workflow_job': single_workflowjob,
            'workflow': self.test_workflow,
        }
        test_connection2 = Connection(**connection2_data)
        test_connection2.save()

        singletons = WorkflowRunList._singleton_workflow_jobs(WorkflowRunList(), self.test_workflow)
        self.assertEqual(singletons, [single_workflowjob])

    def test_get_detail(self):
        response = self.client.get("/workflowrun/eb4b3661be2a44908c4c932b0783bb3e/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list(self):
        response = self.client.get("/workflowruns/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_newly_cancelled(self):
        workflowrun_update = {'cancelled': True}
        self.client.patch("/workflowrun/eb4b3661be2a44908c4c932b0783bb3e/", workflowrun_update, format='json')
        workflowrun_obj = WorkflowRun.objects.get(pk='eb4b3661be2a44908c4c932b0783bb3e')
        expected_status = RunJobStatus.CANCELLED or RunJobStatus.HAS_FINISHED or RunJobStatus.FAILED
        for rj in workflowrun_obj.run_jobs.all():
            self.assertEqual(rj.status, expected_status)
"""
