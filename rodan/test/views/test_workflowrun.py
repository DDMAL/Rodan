import os
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status

from rodan.models.page import Page



class WorkflowRunViewTest(APITestCase):
    fixtures = ["1_users", "2_initial_data"]

    def setUp(self):
        self.media_root = os.path.join(settings.PROJECT_DIR)

        self.client.login(username="ahankins", password="hahaha")
        page = Page.objects.get(uuid="2f63f986449349769d7a313e0fc6edb3")
        page.page_image = SimpleUploadedFile('original_file.png', 'n/t')
        page.compat_page_image = SimpleUploadedFile('compat_page_image.png', 'n/t')
        page.save()

    def test_post(self):
        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/1/',
            'workflow': 'http://localhost:8000/workflow/df78a1aa79554abcb5f1b0ac7bba2bad/',
        }

        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        print(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_no_workflow_ID(self):
        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/1/',
            'workflow': None,
        }

        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {"message": "You must specify a workflow ID"}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_no_existing_workflow(self):
        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/1',
            'workflow': 'http://localhost:8000/workflow/12345/',
        }

        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {"message": "You must specify an existing workflow"}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_no_jobs(self):
        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/1/',
            'workflow': 'http://localhost:8000/workflow/ef78a1aa79554abcb5f1b0ac7bba2bad/',
        }

        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {"message": "No jobs for workflow {0} were specified".format(workflowrun_obj['workflow'])}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_no_pages(self):
        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/1',
            'workflow': 'http://localhost:8000/workflow/ff78a1aa79554abcb5f1b0ac7bba2bad/',
        }

        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {"message": "No pages were assigned to workflow ID {0}".format(workflowrun_obj['workflow'])}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
