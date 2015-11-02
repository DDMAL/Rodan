from rest_framework.test import APITestCase
from rest_framework import status
from rodan.models import WorkflowJob, WorkflowJobGroup
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

    def test_autoset_workflow(self):
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

    def test_create_invalid_wfjgroup(self):
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

    def test_patch_invalid_wfjgroup(self):
        wfjgroup_obj = {
            'workflow_jobs': [
                "http://localhost:8000/workflowjob/{0}/".format(self.test_workflowjob1.uuid)
            ],
            "name": "test group"
        }
        response = self.client.post("/workflowjobgroups/", wfjgroup_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
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
