import os

# import json
import zipfile

# import uuid
import datetime
import socket

from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from model_mommy import mommy

from rodan.constants import task_status
from rodan.models import WorkflowRun, Job, ResultsPackage
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin

bag_metadata = (
    "bag-info.txt",
    "bagit.txt",
    "fetch.txt",
    "manifest-sha1.txt",
    "tagmanifest-sha1.txt",
)


class ResultsPackageViewTest(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.client.force_authenticate(user=self.test_superuser)

    # def test_unfinished_workflowrun(self):
    #     wfr = mommy.make('rodan.WorkflowRun', status=task_status.PROCESSING)
    #     resultspackage_obj = {
    #         'workflow_run': 'http://localhost:8000/workflowrun/{0}/'.format(wfr.uuid),
    #         'packaging_mode': 0
    #     }
    #     response = self.client.post("/api/resultspackages/", resultspackage_obj, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(
    #         response.data,
    #         {'workflow_run': ["Cannot package results of an unfinished or failed WorkflowRun."]}
    #     )

    # def test_nonexist_port(self):
    #     wfr = mommy.make('rodan.WorkflowRun', status=task_status.FINISHED)
    #     resultspackage_obj = {
    #         'workflow_run': 'http://localhost:8000/workflowrun/{0}/'.format(wfr.uuid),
    #         'output_ports': ['http://localhost:8000/api/outputport/{0}/'.format(uuid.uuid1())
    #         ],
    #         'packaging_mode': 0
    #     }
    #     response = self.client.post("/api/resultspackages/", resultspackage_obj, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(response.data, {
    #         'output_ports': [u'Invalid hyperlink - Object does not exist.']})

    def test_post_invalid_status(self):
        wfr = mommy.make("rodan.WorkflowRun", status=task_status.FINISHED)
        resultspackage_obj = {
            "workflow_run": "http://localhost:8000/api/workflowrun/{0}/".format(wfr.uuid),
            "status": task_status.CANCELLED,
            "packaging_mode": 0,
        }
        response = self.client.post(
            "/api/resultspackages/", resultspackage_obj, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "status": [
                    u"Cannot create a cancelled, failed, finished or expired ResultsPackage."
                ]
            },
        )

    def test_patch_cancel(self):
        wfr = mommy.make("rodan.ResultsPackage", status=task_status.SCHEDULED)
        req = {"status": task_status.CANCELLED}
        try:
            response = self.client.patch(
                "/api/resultspackage/{0}/".format(wfr.uuid), req, format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        except socket.error:  # rabbitmq not running
            pass

    def test_patch_invalid_status_update(self):
        wfr = mommy.make("rodan.ResultsPackage", status=task_status.EXPIRED)
        req = {"status": task_status.PROCESSING}
        response = self.client.patch(
            "/api/resultspackage/{0}/".format(wfr.uuid), req, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"status": ["Invalid status update"]})


class ResultsPackageSimpleTest(
    RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin
):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_simple_dummy_workflow()
        self.client.force_authenticate(user=self.test_superuser)
        response = self.client.patch(
            "/api/workflow/{0}/".format(self.test_workflow.uuid),
            {"valid": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Run this dummy workflow
        ra = self.setUp_resources_for_simple_dummy_workflow()
        self.test_resource.resource_file.save(
            "dummy.txt", ContentFile('{"test": "hahaha"}')
        )
        workflowrun_obj = {
            "creator": "http://localhost:8000/api/user/{0}/".format(self.test_user.pk),
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.uuid
            ),
            "resource_assignments": ra,
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wfrun_id = response.data["uuid"]
        dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()

        self.test_user_input = {"foo": "bar"}
        response = self.client.post(
            "/api/interactive/{0}/".format(str(dummy_m_runjob.uuid)), self.test_user_input
        )
        self.test_workflowrun = WorkflowRun.objects.get(uuid=wfrun_id)
        # self.assertEqual(self.test_workflowrun.status, task_status.SCHEDULED)
        # workflowrun_update = {'status': task_status.REQUEST_PROCESSING}
        # response = self.client.patch(
        #     "/workflowrun/{0}/".format(str(wfrun_id)), workflowrun_update, format='json')
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(self.test_workflowrun.status, task_status.FINISHED)
        self.output_a = self.dummy_a_wfjob.run_jobs.first().outputs.first()
        self.output_m = self.dummy_m_wfjob.run_jobs.first().outputs.first()

    def test_all_ports(self):
        resultspackage_obj = {
            "workflow_run": "http://localhost:8000/api/workflowrun/{0}/".format(
                self.test_workflowrun.uuid
            ),
            "output_ports": [
                "http://localhost:8000/api/outputport/{0}/".format(
                    self.output_a.output_port.uuid
                ),
                "http://localhost:8000/api/outputport/{0}/".format(
                    self.output_m.output_port.uuid
                ),
            ],
            "packaging_mode": 0,
        }
        response = self.client.post(
            "/api/resultspackages/", resultspackage_obj, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        rp_id = response.data["uuid"]
        rp = ResultsPackage.objects.get(uuid=rp_id)
        # print(rp.error_summary, rp.error_details)
        self.assertEqual(rp.status, task_status.FINISHED)
        self.assertEqual(rp.percent_completed, 100)
        self.assertEqual(os.path.isfile(rp.package_path), True)
        with zipfile.ZipFile(rp.package_path, "r") as z:
            files = z.namelist()
        files = filter(lambda f: f not in bag_metadata, files)
        # self.assertEqual(len(files), 2)
        # print(files)
        # TODO: test file names

    def test_one_port(self):
        resultspackage_obj = {
            "workflow_run": "http://localhost:8000/api/workflowrun/{0}/".format(
                self.test_workflowrun.uuid
            ),
            "output_ports": [
                "http://localhost:8000/api/outputport/{0}/".format(
                    self.output_a.output_port.uuid
                )
            ],
            "packaging_mode": 0,
        }
        response = self.client.post(
            "/api/resultspackages/", resultspackage_obj, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        rp_id = response.data["uuid"]
        rp = ResultsPackage.objects.get(uuid=rp_id)
        self.assertEqual(rp.status, task_status.FINISHED)
        self.assertEqual(rp.percent_completed, 100)
        self.assertEqual(os.path.isfile(rp.package_path), True)
        with zipfile.ZipFile(rp.package_path, "r") as z:
            files = z.namelist()
        files = filter(lambda f: f not in bag_metadata, files)
        # self.assertEqual(len(files), 1)
        # print(files)
        # TODO: test file names

    # def test_invalid_port(self):
    #     invalid_op = mommy.make('rodan.OutputPort')
    #     resultspackage_obj = {
    #         'workflow_run': 'http://localhost:8000/workflowrun/{0}/'.format(
    #             self.test_workflowrun.uuid
    #         ),
    #         'output_ports': [
    #             'http://localhost:8000/api/outputport/{0}/'.format(invalid_op.uuid)
    #         ],
    #         'packaging_mode': 0
    #     }
    #     response = self.client.post("/api/resultspackages/", resultspackage_obj, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(
    #         response.data,
    #         {
    #             u'non_field_errors': [
    #                 (
    #                     "Confliction between WorkflowRun and OutputPort: OutputPort {0} not in"
    #                     " WorkflowRun {1}'s Workflow."
    #                 ).format(
    #                     invalid_op.uuid,
    #                     self.test_workflowrun.uuid
    #                 )
    #             ]
    #         }
    #     )


class ResultsPackageComplexTest(
    RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin
):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_complex_dummy_workflow()
        self.client.force_authenticate(user=self.test_superuser)

        # modify all manual job to automatic to save effort (and in/output ports)
        from rodan.test.dummy_jobs import dummy_automatic_job

        # from rodan.test.dummy_jobs import dummy_manual_job

        job_a = Job.objects.get(name=dummy_automatic_job.name)
        # job_m = Job.objects.get(name=dummy_manual_job.name)

        ipt_aA = job_a.input_port_types.get(name="in_typeA")
        ipt_aB = job_a.input_port_types.get(name="in_typeB")
        ipt_aL = job_a.input_port_types.get(name="in_typeL")
        opt_aA = job_a.output_port_types.get(name="out_typeA")
        # opt_aB = job_a.output_port_types.get(name="out_typeB")
        opt_aL = job_a.output_port_types.get(name="out_typeL")

        self.test_wfjob_B.job = job_a
        self.test_wfjob_B.save()
        self.test_wfjob_D.job = job_a
        self.test_wfjob_D.save()

        self.test_Bop.output_port_type = opt_aL
        self.test_Bop.save()
        self.test_Dip1.input_port_type = ipt_aA
        self.test_Dip1.save()
        self.test_Dip2.input_port_type = ipt_aB
        self.test_Dip2.save()
        self.test_Dip3.input_port_type = ipt_aL
        self.test_Dip3.save()
        self.test_Dop.output_port_type = opt_aA
        self.test_Dop.save()

        response = self.client.patch(
            "/api/workflow/{0}/".format(self.test_workflow.uuid),
            {"valid": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Run this dummy workflow
        ra = self.setUp_resources_for_complex_dummy_workflow()
        workflowrun_obj = {
            "creator": "http://localhost:8000/user/{0}/".format(self.test_superuser.pk),
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.uuid
            ),
            "resource_assignments": ra,
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wfrun_id = response.data["uuid"]
        self.test_workflowrun = WorkflowRun.objects.get(uuid=wfrun_id)

        # self.assertEqual(self.test_workflowrun.status, task_status.SCHEDULED)
        # self.assertEqual(self.test_workflowrun.status, task_status.PROCESSING)

        # workflowrun_update = {'status': task_status.REQUEST_PROCESSING}
        # response = self.client.patch(
        #     "/workflowrun/{0}/".format(
        #         str(wfrun_id)),
        #         workflowrun_update,
        #         format='json'
        #     )
        # self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_workflowrun = WorkflowRun.objects.get(uuid=wfrun_id)
        self.assertEqual(self.test_workflowrun.status, task_status.FINISHED)

    def test_one_port(self):
        resultspackage_obj = {
            "workflow_run": "http://localhost:8000/api/workflowrun/{0}/".format(
                self.test_workflowrun.uuid
            ),
            "output_ports": [
                "http://localhost:8000/api/outputport/{0}/".format(self.test_Fop.uuid)
            ],
            "packaging_mode": 0,
        }
        response = self.client.post(
            "/api/resultspackages/", resultspackage_obj, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        rp_id = response.data["uuid"]
        rp = ResultsPackage.objects.get(uuid=rp_id)
        self.assertEqual(rp.status, task_status.FINISHED)
        self.assertEqual(rp.percent_completed, 100)

        self.assertEqual(os.path.isfile(rp.package_path), True)
        with zipfile.ZipFile(rp.package_path, "r") as z:
            files = z.namelist()
        files = filter(lambda f: f not in bag_metadata, files)
        # self.assertEqual(len(files), 10)
        # print(files)
        # TODO: test file names

    def test_default_ports(self):
        resultspackage_obj = {
            "workflow_run": "http://localhost:8000/api/workflowrun/{0}/".format(
                self.test_workflowrun.uuid
            ),
            "packaging_mode": 0,
        }
        response = self.client.post(
            "/api/resultspackages/", resultspackage_obj, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # rp_id = response.data['uuid']
        # rp = ResultsPackage.objects.get(uuid=rp_id)
        # self.assertEqual(
        #     set([self.test_Cop2, self.test_Fop, self.test_Eop]), set(rp.output_ports.all()))

    def test_expire(self):
        resultspackage_obj = {
            "workflow_run": "http://localhost:8000/api/workflowrun/{0}/".format(
                self.test_workflowrun.uuid
            ),
            "output_ports": [
                "http://localhost:8000/api/outputport/{0}/".format(self.test_Fop.uuid)
            ],
            "expiry_time": datetime.datetime.now() + datetime.timedelta(minutes=1),
            "packaging_mode": 0,
        }
        response = self.client.post(
            "/api/resultspackages/", resultspackage_obj, format="json"
        )
        rp_id = response.data["uuid"]
        rp = ResultsPackage.objects.get(uuid=rp_id)
        self.assertEqual(
            rp.status, task_status.EXPIRED
        )  # in test, scheduled expiry task is eagerly executed
        self.assertEqual(os.path.isfile(rp.package_path), False)
