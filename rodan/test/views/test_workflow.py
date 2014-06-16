import os
from django.conf import settings
from django.contrib.auth.models import User

from rodan.models.project import Project
from rodan.models.workflowjob import WorkflowJob
from rodan.models.workflow import Workflow
from rodan.models.resourceassignment import ResourceAssignment
from rodan.models.inputport import InputPort
from rodan.models.resource import Resource

from rest_framework.test import APITestCase
from rest_framework import status


class WorkflowViewTestCase(APITestCase):
    fixtures = ["1_users", "2_initial_data"]

    def setUp(self):
        self.media_root = os.path.join(settings.PROJECT_DIR)

        self.client.login(username="ahankins", password="hahaha")
        self.test_user = User.objects.get(username="ahankins")
        self.test_project = Project.objects.get(uuid="9e8e928b4ec24a09b6113f1b0af1ea53")
        self.test_inputport = InputPort.objects.get(uuid="e38b11918691486cbd99627e5baec0a1")
        self.test_workflowjobs = WorkflowJob.objects.all()
        self.test_resources = Resource.objects.filter(workflow=Workflow.objects.get(uuid="ff78a1aa79554abcb5f1b0ac7bba2bad"))
        self.test_resourceassignment = ResourceAssignment.objects.get(uuid="cfda287923344720bfbec39081819617")

    def test_validate_no_workflowjobs(self):
        workflow_update = {
            'valid': True,
            'workflow_job_set': None,
        }
        response = self.client.patch("/workflow/ff78a1aa79554abcb5f1b0ac7bba2bad/", workflow_update, format='json')
        anticipated_message = {'message': 'No WorkflowJobs in Workflow'}
        retr_workflow = Workflow.objects.get(pk="ff78a1aa79554abcb5f1b0ac7bba2bad")
        self.assertEqual(response.data, anticipated_message)
        self.assertFalse(retr_workflow.valid)

    def test_validate_multiple_resource_collections(self):
        test_resourceassignment2 = ResourceAssignment(input_port=self.test_inputport, workflow=Workflow.objects.get(uuid="ff78a1aa79554abcb5f1b0ac7bba2bad"))
        test_resourceassignment2.save()
        for res in self.test_resources:
            test_resourceassignment2.resources.add(res)
            test_resourceassignment2.save()

        workflow_update = {
            'valid': True,
            'workflow_job_set': [
                'http://localhost:8000/workflowjob/a21f510a16c24701ac0e435b3f4c20f2/',
            ],
        }

        response = self.client.patch("/workflow/ff78a1aa79554abcb5f1b0ac7bba2bad/", workflow_update, format='json')
        anticipated_message = {'message': 'Multiple resource assignment collections found'}
        retr_workflow = Workflow.objects.get(pk="ff78a1aa79554abcb5f1b0ac7bba2bad")
        self.assertEqual(response.data, anticipated_message)
        self.assertFalse(retr_workflow.valid)

    def test_no_posting_valid(self):
        workflow_obj = {
            'project': 'http://localhost:8000/project/9e8e928b4ec24a09b6113f1b0af1ea53/',
            'name': "test workflow",
            'creator': 'http://localhost:8000/user/1/',
            'valid': True,
            'workflow_job_set': [
                'http://localhost:8000/workflowjob/a21f510a16c24701ac0e435b3f4c20f2/',
            ],
        }
        response = self.client.post("/workflows/", workflow_obj, format='json')
        anticipated_message = {'message': "You can't POST a valid workflow - it must be validated through a PATCH request"}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validate_resources_not_in_workflow(self):
        test_orphan_resource = Resource.objects.get(pk="8aa7e270b1c54be49dde5a682b16cda7")
        test_resourceassignment2 = ResourceAssignment(input_port=self.test_inputport, workflow=Workflow.objects.get(uuid="ff78a1aa79554abcb5f1b0ac7bba2bad"))
        test_resourceassignment2.save()
        test_resourceassignment2.resources.add(test_orphan_resource)

        workflow_update = {
            'valid': True,
            'workflow_job_set': [
                'http://localhost:8000/workflowjob/a21f510a16c24701ac0e435b3f4c20f2/',
            ],
        }
        response = self.client.patch("/workflow/ff78a1aa79554abcb5f1b0ac7bba2bad/", workflow_update, format='json')
        anticipated_message = {'message': 'The resource {0} is not in the workflow'.format(test_orphan_resource.name)}
        retr_workflow = Workflow.objects.get(pk="ff78a1aa79554abcb5f1b0ac7bba2bad")
        self.assertEqual(response.data, anticipated_message)
        self.assertFalse(retr_workflow.valid)
