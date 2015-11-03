from rest_framework.test import APITestCase
from rest_framework import status
from rodan.models import WorkflowJob, WorkflowJobGroup, InputPort, OutputPort, Connection, Workflow
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
from model_mommy import mommy


class WorkflowJobGroupViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.test_workflow1 = mommy.make('rodan.Workflow')
        self.test_workflow2 = mommy.make('rodan.Workflow')
        self.test_workflowjob1 = mommy.make('rodan.WorkflowJob', workflow=self.test_workflow1)
        self.test_workflowjob1b = mommy.make('rodan.WorkflowJob', workflow=self.test_workflow1)
        self.test_workflowjob2 = mommy.make('rodan.WorkflowJob', workflow=self.test_workflow2)
        self.client.force_authenticate(user=self.test_superuser)

    def test_create_and_autoset_workflow(self):
        wfjgroup_obj = {
            'workflow_jobs': [
                "http://localhost:8000/workflowjob/{0}/".format(self.test_workflowjob1.uuid),
                "http://localhost:8000/workflowjob/{0}/".format(self.test_workflowjob1b.uuid)
            ],
            "name": "test group"
        }
        response = self.client.post("/workflowjobgroups/", wfjgroup_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wfjgroup_uuid = response.data['uuid']
        wfjg = WorkflowJobGroup.objects.get(uuid=wfjgroup_uuid)
        self.assertEqual(wfjg.workflow, self.test_workflow1)

        wfjgroup_obj = {
            'workflow_jobs': [
                "http://localhost:8000/workflowjob/{0}/".format(self.test_workflowjob2.uuid)
            ]
        }
        response = self.client.patch("/workflowjobgroup/{0}/".format(wfjgroup_uuid), wfjgroup_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        wfjg = WorkflowJobGroup.objects.get(uuid=wfjgroup_uuid)  # refetch
        self.assertEqual(wfjg.workflow, self.test_workflow2)

    def test_create_conflict_wfjgroup(self):
        wfjgroup_obj = {
            'workflow_jobs': [
                "http://localhost:8000/workflowjob/{0}/".format(self.test_workflowjob1.uuid),
                "http://localhost:8000/workflowjob/{0}/".format(self.test_workflowjob2.uuid)
            ],
            "name": "test group"
        }
        response = self.client.post("/workflowjobgroups/", wfjgroup_obj, format='json')
        anticipated_message = {'workflow_jobs': ["All WorkflowJobs should belong to the same Workflow."]}

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_patch_conflict_wfjgroup(self):
        wfjgroup_obj = {
            'workflow_jobs': [
                "http://localhost:8000/workflowjob/{0}/".format(self.test_workflowjob1.uuid)
            ],
            "name": "test group"
        }
        response = self.client.post("/workflowjobgroups/", wfjgroup_obj, format='json')
        assert response.status_code == status.HTTP_201_CREATED, 'This should pass'
        wfjgroup_uuid = response.data['uuid']

        wfjgroup_obj = {
            'workflow_jobs': [
                "http://localhost:8000/workflowjob/{0}/".format(self.test_workflowjob1.uuid),
                "http://localhost:8000/workflowjob/{0}/".format(self.test_workflowjob2.uuid)
            ]
        }
        response = self.client.patch("/workflowjobgroup/{0}/".format(wfjgroup_uuid), wfjgroup_obj, format='json')
        anticipated_message = {'workflow_jobs': ["All WorkflowJobs should belong to the same Workflow."]}

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_create_empty_workflowjobgroup(self):
        wfjgroup_obj = {
            'workflow_jobs': [],
            'name': 'empty group'
        }
        response = self.client.post("/workflowjobgroups/", wfjgroup_obj, format='json')
        anticipated_message = {'workflow_jobs': ["Empty WorkflowJobGroup is not allowed."]}

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_patch_empty_workflowjobgroup(self):
        wfjgroup_obj = {
            'workflow_jobs': [
                "http://localhost:8000/workflowjob/{0}/".format(self.test_workflowjob1.uuid)
            ],
            "name": "test group"
        }
        response = self.client.post("/workflowjobgroups/", wfjgroup_obj, format='json')
        assert response.status_code == status.HTTP_201_CREATED, 'This should pass'
        wfjgroup_uuid = response.data['uuid']

        wfjgroup_obj = {
            'workflow_jobs': []
        }
        response = self.client.patch("/workflowjobgroup/{0}/".format(wfjgroup_uuid), wfjgroup_obj, format='json')
        anticipated_message = {'workflow_jobs': ["Empty WorkflowJobGroup is not allowed."]}

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)



class WorkflowJobGroupActionTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_complex_dummy_workflow()
        self.client.force_authenticate(user=self.test_superuser)

    def test_import_valid_workflow(self):
        self.test_workflow.valid = True
        self.test_workflow.save()
        self.test_new_workflow = mommy.make('rodan.Workflow')
        mommy.make('rodan.WorkflowJob', workflow=self.test_new_workflow)  # make it non-null
        wfjgroup_obj = {
            'workflow': "http://localhost:8000/workflow/{0}/".format(self.test_new_workflow.pk),
            'origin': "http://localhost:8000/workflow/{0}/".format(self.test_workflow.pk),
        }
        response = self.client.post("/workflowjobgroups/", wfjgroup_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wfjgroup_uuid = response.data['uuid']

        # Check object numbers
        self.assertEqual(WorkflowJob.objects.filter(workflow=self.test_new_workflow).count(), 6+1)
        self.assertEqual(InputPort.objects.filter(workflow_job__workflow=self.test_new_workflow).count(), 10)
        self.assertEqual(OutputPort.objects.filter(workflow_job__workflow=self.test_new_workflow).count(), 7)
        self.assertEqual(Connection.objects.filter(input_port__workflow_job__workflow=self.test_new_workflow).count(), 6)

    def test_import_invalid_workflow(self):
        self.test_workflow.valid = False
        self.test_workflow.save()
        self.test_new_workflow = mommy.make('rodan.Workflow')
        mommy.make('rodan.WorkflowJob', workflow=self.test_new_workflow)  # make it non-null
        wfjgroup_obj = {
            'workflow': "http://localhost:8000/workflow/{0}/".format(self.test_new_workflow.pk),
            'origin': "http://localhost:8000/workflow/{0}/".format(self.test_workflow.pk),
        }
        response = self.client.post("/workflowjobgroups/", wfjgroup_obj, format='json')
        anticipated_message = {'origin': ["Origin workflow must be valid."]}

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_export_workflowjobgroup(self):
        wfjgroup_obj = {
            'workflow_jobs': [
                "http://localhost:8000/workflowjob/{0}/".format(self.test_wfjob_A.uuid),
                "http://localhost:8000/workflowjob/{0}/".format(self.test_wfjob_B.uuid),
                "http://localhost:8000/workflowjob/{0}/".format(self.test_wfjob_C.uuid),
            ],
            'name': 'hahaha'
        }
        response = self.client.post("/workflowjobgroups/", wfjgroup_obj, format='json')
        assert response.status_code == status.HTTP_201_CREATED, 'This should pass'
        wfjgroup_uuid = response.data['uuid']

        project = mommy.make('rodan.Project')
        wf_obj = {
            'workflow_job_group': "http://localhost:8000/workflowjobgroup/{0}/".format(wfjgroup_uuid),
            'project': "http://localhost:8000/project/{0}/".format(project.pk)
        }
        response = self.client.post("/workflows/", wf_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wf_uuid = response.data['uuid']
        wf = Workflow.objects.get(uuid=wf_uuid)

        # Check object numbers
        self.assertEqual(WorkflowJob.objects.filter(workflow=wf).count(), 3)
        self.assertEqual(InputPort.objects.filter(workflow_job__workflow=wf).count(), 3)
        self.assertEqual(OutputPort.objects.filter(workflow_job__workflow=wf).count(), 4)
        self.assertEqual(Connection.objects.filter(input_port__workflow_job__workflow=wf).count(), 2)
