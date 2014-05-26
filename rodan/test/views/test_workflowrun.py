import os
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
import rodan.jobs.devel.dummy_job

from rodan.models.page import Page
from rodan.models.project import Project
from rodan.models.workflow import Workflow
from rodan.models.workflowrun import WorkflowRun
from rodan.models.workflowjob import WorkflowJob

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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_post_no_workflow_ID(self):
    #     workflowrun_obj = {
    #         'creator': 'http://localhost:8000/user/1/',
    #         'workflow': None,
    #     }

    #     response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_no_existing_workflow(self):
        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/1',
            'workflow': 'http://localhost:8000/workflow/not_a_real_pk',
        }

        response = self.client.post("workflowruns/", workflowrun_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # def test_post_no_jobs(self):
    #     # I added a workflow to the fixtures that doesn't have any jobs associated with it
    #     # Maybe I should rather instatiate a new workflow here like that instead of having it in the fixture?
    #     # I'm not really sure how to do that though
    #     workflow_obj = {
    #         'name': 'Test workflow - no jobs',
    #         'creator': 'http://localhost:8000/user/1/',
    #         'pages': 'http://localhost:8000/page/2f63f986449349769d7a313e0fc6edb3/',
    #         'project': 'http://localhost:8000/project/9e8e928b4ec24a09b6113f1b0af1ea53/',
    #     }

        # workflow = Workflow.objects.create(workflow_obj)

        # workflowrun_obj = {
        #     'creator': 'http://localhost:8000/user/1/',
        #     'workflow': workflow_obj,
        # }

        # response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Because I can't create any workflowruns on my server right now I'm just checking that
        # the workflow that will eventually be tested in this method has no jobs associated with it.
        # Once the posting gets fixed the above (commented) two lines of code should work.
        
        # workflow_jobs = WorkflowJob.objects.filter(workflow=workflow_obj)
        # self.assertEqual(workflow_jobs.exists(), False)

