import os, json, zipfile, uuid, datetime, socket
from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework import status

from rodan.models import WorkflowRun, Workflow, WorkflowJob, InputPort, InputPortType, OutputPort, OutputPortType, Connection, Job, RunJob, ResourceType, ResultsPackage
from model_mommy import mommy
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
import uuid
from django.core.files.base import ContentFile
from rodan.models.resource import upload_path
from rodan.constants import task_status

bag_metadata = ('bag-info.txt', 'bagit.txt', 'fetch.txt', 'manifest-sha1.txt', 'tagmanifest-sha1.txt')

class ResultsPackageViewTest(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.client.login(username="super", password="hahaha")

    def test_unfinished_workflowrun(self):
        wfr = mommy.make('rodan.WorkflowRun', status=task_status.PROCESSING)
        resultspackage_obj = {
            'workflow_run': 'http://localhost:8000/workflowrun/{0}/'.format(wfr.uuid.hex),
            'packaging_mode': 0
        }
        response = self.client.post("/resultspackages/", resultspackage_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'workflow_run': ["Cannot package results of an unfinished or failed WorkflowRun."]})

    """
    def test_nonexist_port(self):
        wfr = mommy.make('rodan.WorkflowRun', status=task_status.FINISHED)
        resultspackage_obj = {
            'workflow_run': 'http://localhost:8000/workflowrun/{0}/'.format(wfr.uuid.hex),
            'output_ports': ['http://localhost:8000/outputport/{0}/'.format(uuid.uuid1().hex)
            ]
        }
        response = self.client.post("/resultspackages/", resultspackage_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'output_ports': [u'Invalid hyperlink - Object does not exist.']})
    """

    def test_post_invalid_status(self):
        wfr = mommy.make('rodan.WorkflowRun', status=task_status.FINISHED)
        resultspackage_obj = {
            'workflow_run': 'http://localhost:8000/workflowrun/{0}/'.format(wfr.uuid.hex),
            'status': task_status.CANCELLED,
            'packaging_mode': 0
        }
        response = self.client.post("/resultspackages/", resultspackage_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'status': [u"Cannot create a cancelled, failed, finished or expired ResultsPackage."]})


    def test_patch_cancel(self):
        wfr = mommy.make('rodan.ResultsPackage', status=task_status.SCHEDULED)
        req = {
            'status': task_status.CANCELLED
        }
        try:
            response = self.client.patch("/resultspackage/{0}/".format(wfr.uuid.hex), req, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        except socket.error:   # rabbitmq not running
            pass

    def test_patch_invalid_status_update(self):
        wfr = mommy.make('rodan.ResultsPackage', status=task_status.EXPIRED)
        req = {
            'status': task_status.PROCESSING
        }
        response = self.client.patch("/resultspackage/{0}/".format(wfr.uuid.hex), req, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'status': ["Invalid status update"]})


class ResultsPackageSimpleTest(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_simple_dummy_workflow()
        self.client.login(username="super", password="hahaha")

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

    """
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

        self.assertEqual(os.path.isfile(rp.package_path), True)
        with zipfile.ZipFile(rp.package_path, 'r') as z:
            files = z.namelist()
        files = filter(lambda f: f not in bag_metadata, files)
        self.assertEqual(len(files), 2)
        #print files
        # TODO: test file names
    def test_one_port(self):
        resultspackage_obj = {
            'workflow_run': 'http://localhost:8000/workflowrun/{0}/'.format(self.test_workflowrun.uuid),
            'output_ports': ['http://localhost:8000/outputport/{0}/'.format(self.output_a.output_port.uuid)
            ]
        }
        response = self.client.post("/resultspackages/", resultspackage_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        rp_id = response.data['uuid']
        rp = ResultsPackage.objects.get(uuid=rp_id)
        self.assertEqual(rp.status, task_status.FINISHED)
        self.assertEqual(rp.percent_completed, 100)

        self.assertEqual(os.path.isfile(rp.package_path), True)
        with zipfile.ZipFile(rp.package_path, 'r') as z:
            files = z.namelist()
        files = filter(lambda f: f not in bag_metadata, files)
        self.assertEqual(len(files), 1)
        #print files
        # TODO: test file names

    def test_invalid_port(self):
        invalid_op = mommy.make('rodan.OutputPort')
        resultspackage_obj = {
            'workflow_run': 'http://localhost:8000/workflowrun/{0}/'.format(self.test_workflowrun.uuid.hex),
            'output_ports': ['http://localhost:8000/outputport/{0}/'.format(invalid_op.uuid.hex)
            ]
        }
        response = self.client.post("/resultspackages/", resultspackage_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {u'non_field_errors': ["Confliction between WorkflowRun and OutputPort: OutputPort {0} not in WorkflowRun {1}'s Workflow.".format(invalid_op.uuid.hex, self.test_workflowrun.uuid.hex)]})
    """


class ResultsPackageComplexTest(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_complex_dummy_workflow()
        self.client.login(username="super", password="hahaha")

        # modify all manual job to automatic to save effort (and in/output ports)
        job_a = self.test_wfjob_A.job
        self.test_wfjob_B.job = job_a
        self.test_wfjob_B.save()
        self.test_wfjob_D.job = job_a
        self.test_wfjob_D.save()

        ipt_aA = self.test_Aip.input_port_type
        ipt_aB = self.test_Cip2.input_port_type
        opt_aA = self.test_Aop.output_port_type
        self.test_Bop.output_port_type = opt_aA
        self.test_Bop.save()
        self.test_Dip1.input_port_type = ipt_aA
        self.test_Dip1.save()
        self.test_Dip2.input_port_type = ipt_aB
        self.test_Dip2.save()
        self.test_Dip3.input_port_type = ipt_aA
        self.test_Dip3.save()
        self.test_Dop.output_port_type = opt_aA
        self.test_Dop.save()

        # Run this dummy workflow
        response = self.client.patch("/workflow/{0}/".format(self.test_workflow.uuid), {'valid': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/{0}/'.format(self.test_user.pk),
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid)
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wfrun_id = response.data['uuid']
        self.test_workflowrun = WorkflowRun.objects.get(uuid=wfrun_id)
        self.assertEqual(self.test_workflowrun.status, task_status.FINISHED)

    """
    def test_one_port(self):
        resultspackage_obj = {
            'workflow_run': 'http://localhost:8000/workflowrun/{0}/'.format(self.test_workflowrun.uuid),
            'output_ports': ['http://localhost:8000/outputport/{0}/'.format(self.test_Fop.uuid)
            ]
        }
        response = self.client.post("/resultspackages/", resultspackage_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        rp_id = response.data['uuid']
        rp = ResultsPackage.objects.get(uuid=rp_id)
        self.assertEqual(rp.status, task_status.FINISHED)
        self.assertEqual(rp.percent_completed, 100)

        self.assertEqual(os.path.isfile(rp.package_path), True)
        with zipfile.ZipFile(rp.package_path, 'r') as z:
            files = z.namelist()
        files = filter(lambda f: f not in bag_metadata, files)
        self.assertEqual(len(files), 10)
        #print files
        # TODO: test file names

    def test_default_ports(self):
        resultspackage_obj = {
            'workflow_run': 'http://localhost:8000/workflowrun/{0}/'.format(self.test_workflowrun.uuid)
        }
        response = self.client.post("/resultspackages/", resultspackage_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        rp_id = response.data['uuid']
        rp = ResultsPackage.objects.get(uuid=rp_id)
        self.assertEqual(set([self.test_Cop2, self.test_Fop, self.test_Eop]), set(rp.output_ports.all()))
    """

    def test_expire(self):
        resultspackage_obj = {
            'workflow_run': 'http://localhost:8000/workflowrun/{0}/'.format(self.test_workflowrun.uuid),
            'output_ports': ['http://localhost:8000/outputport/{0}/'.format(self.test_Fop.uuid)
                         ],
            'expiry_time': datetime.datetime.now() + datetime.timedelta(minutes=1),
            'packaging_mode': 0
        }
        response = self.client.post("/resultspackages/", resultspackage_obj, format='json')
        rp_id = response.data['uuid']
        rp = ResultsPackage.objects.get(uuid=rp_id)
        self.assertEqual(rp.status, task_status.EXPIRED)  # in test, scheduled expiry task is eagerly executed
        self.assertEqual(os.path.isfile(rp.package_path), False)
