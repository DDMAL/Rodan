from django.test import TestCase
from rodan.models.project import Project
from django.contrib.auth.models import User
from rodan.models.workflow import Workflow
from rodan.models.workflowrun import WorkflowRun
from rodan.models.workflowjob import WorkflowJob
from rodan.models.page import Page
from rodan.models.runjob import RunJob
from rodan.models.job import Job


class RunJobTestCase(TestCase):
    fixtures = ["1_users", "2_initial_data"]

    def setUp(self):
        self.test_workflowrun = WorkflowRun.objects.get(uuid="eb4b3661be2a44908c4c932b0783bb3e")
        self.test_workflowjob = WorkflowJob.objects.get(uuid="a21f510a16c24701ac0e435b3f4c20f2")
        self.test_page = Page.objects.get(uuid="2f63f986449349769d7a313e0fc6edb3")

    def test_save(self):
        test_runjob = RunJob(workflow_run=self.test_workflowrun, workflow_job=self.test_workflowjob, page=self.test_page)
        test_runjob.save()

        retr_runjob = RunJob.objects.get(uuid=test_runjob.pk)
        self.assertEqual(retr_runjob, test_runjob)

        retr_runjob.delete()

    def test_delete(self):
        pass