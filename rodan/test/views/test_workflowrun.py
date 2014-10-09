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
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
import uuid
from django.core.files.base import ContentFile
from rodan.models.resource import upload_path

class WorkflowRunViewTest(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_dummy_workflow()
        self.client.login(username="ahankins", password="hahaha")
        self.client.patch("/workflow/{0}/".format(self.test_workflow.uuid), {'valid': True}, format='json')

    def test_get_list(self):
        response = self.client.get("/workflowruns/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_no_workflow_ID(self):
        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/{0}/'.format(self.test_user.pk)
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
        workflowrun_update = {'cancelled': True}
        response = self.client.patch("/workflowrun/{0}/".format(uuid.uuid1()), workflowrun_update, format='json')
        anticipated_message = {'message': 'Workflow_run not found'}
        self.assertEqual(anticipated_message, response.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



class WorkflowRunExecutionTest(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_dummy_workflow()
        self.client.login(username="ahankins", password="hahaha")
        self.client.patch("/workflow/{0}/".format(self.test_workflow.uuid), {'valid': True}, format='json')


    def test_successful_execution(self):
        with self.settings(CELERY_ALWAYS_EAGER=True,
                           CELERY_EAGER_PROPAGATES_EXCEPTIONS=True):  # run celery task locally

            self.test_resource.resource_file.save('dummy.txt', ContentFile('dummy text'))
            self.test_resource.compat_resource_file.save('dummy.txt', ContentFile('dummy text'))

            workflowrun_obj = {
                'creator': 'http://localhost:8000/user/{0}/'.format(self.test_user.pk),
                'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            }
            response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            dummy_a_runjob = self.dummy_a_wfjob.run_jobs.first()
            dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()

            # At this point, the automatic RunJob should be finished, and the manual RunJob should accept input
            self.assertEqual(dummy_a_runjob.status, RunJobStatus.HAS_FINISHED)
            self.assertEqual(dummy_m_runjob.status, RunJobStatus.NOT_RUNNING)
            self.assertEqual(dummy_m_runjob.ready_for_input, True)

            response = self.client.post("/interactive/poly_mask/", {'run_job_uuid': str(dummy_m_runjob.uuid)})
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # then the workflowrun should re-run
            dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()  # refetch
            self.assertEqual(dummy_m_runjob.status, RunJobStatus.HAS_FINISHED)

    def test_failed_execution(self):
        with self.settings(CELERY_ALWAYS_EAGER=True):  # run celery task locally
            self.test_resource.resource_file.save('dummy.txt', ContentFile('will fail'))
            self.test_resource.compat_resource_file.save('dummy.txt', ContentFile('will fail'))
            workflowrun_obj = {
                'creator': 'http://localhost:8000/user/{0}/'.format(self.test_user.pk),
                'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            }

            response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            dummy_a_runjob = self.dummy_a_wfjob.run_jobs.first()
            dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()

            # At this point, the automatic RunJob should be finished, and the manual RunJob should accept input
            self.assertEqual(dummy_a_runjob.status, RunJobStatus.FAILED)
            self.assertEqual(dummy_a_runjob.error_summary, 'dummy automatic job error')
            self.assertEqual(dummy_m_runjob.status, RunJobStatus.NOT_RUNNING)
            self.assertEqual(dummy_m_runjob.ready_for_input, False)

    def test_cancel(self):
        with self.settings(CELERY_ALWAYS_EAGER=True,
                           CELERY_EAGER_PROPAGATES_EXCEPTIONS=True):  # run celery task locally
            self.test_resource.resource_file.save('dummy.txt', ContentFile('dummy text'))
            self.test_resource.compat_resource_file.save('dummy.txt', ContentFile('dummy text'))
            workflowrun_obj = {
                'creator': 'http://localhost:8000/user/{0}/'.format(self.test_user.pk),
                'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            }
            response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
            wfrun_uuid = response.data['uuid']

            response = self.client.patch("/workflowrun/{0}/".format(wfrun_uuid), {'cancelled': True}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()
            self.assertEqual(dummy_m_runjob.status, RunJobStatus.CANCELLED)

            workflowrun_update = {'cancelled': False}
            response = self.client.patch("/workflowrun/{0}/".format(wfrun_uuid), workflowrun_update, format='json')
            anticipated_message = {"message": "Workflowrun cannot be uncancelled."}
            self.assertEqual(anticipated_message, response.data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



"""
    def test_get_detail(self):
        response = self.client.get("/workflowrun/eb4b3661be2a44908c4c932b0783bb3e/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
"""

"""
_threads = {}

def setUpModule():
    _threads['celery'] = CeleryWorkerThread()
    _threads['celery'].daemon = True
    _threads['celery'].start()

    # Wait for the worker to be ready
    _threads['celery'].is_ready.wait()
    if _threads['celery'].error:
        raise _threads['celery'].error


def tearDownModule():
    if 'celery' in _threads:
        _threads['celery'].join(5)
"""
