from django.test import TestCase
from django.contrib.auth.models import User
from rodan.models.project import Project
from rodan.models.workflow import Workflow
from rodan.models.workflowjob import WorkflowJob


class WorkflowViewTestCase(TestCase):
    fixtures = ["1_users", "2_initial_data"]

    def setUp(self):
        self.test_user = User.objects.get(username="ahankins")
        self.test_project = Project.objects.get(uuid="9e8e928b4ec24a09b6113f1b0af1ea53")
        self.test_workflowjob = WorkflowJob.objects.get(uuid="a21f510a16c24701ac0e435b3f4c20f2")

    def test_validate_no_workflowjobs(self):
        workflow_update = {
            'valid': True,
            'workflow_jobs': None,
        }
        response = self.client.patch("/workflow/26612acba44d41df9bc987a5e89d3b7b/", request=workflow_update, format='json')
        anticipated_message = {"message": "No WorkflowJobs in Workflow"}
        self.assertEqual(response.data, anticipated_message)
        retr_workflow = Workflow.objects.get(pk="26612acba44d41df9bc987a5e89d3b7b")
        self.assertFalse(retr_workflow.valid)

    def test_validate_multiple_resource_collections(self):
        workflow_update = {
            'valid': True,
            'workflow_jobs': self.test_workflowjob,
            'resource_assignment': [
                
            ]
        }
        self.client.patch("/workflow/26612acba44d41df9bc987a5e89d3b7b/", request=workflow_update, format='json')
        retr_workflow = Workflow.objects.get(pk="26612acba44d41df9bc987a5e89d3b7b")
        self.assertFalse(retr_workflow.valid)
