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
    def setUp(self):
        self.test_user = User(username="test user")
        self.test_user.save()

        self.test_project = Project(name="test project", creator=self.test_user)
        self.test_project.save()

        self.test_page = Page(name="test page", project=self.test_project)
        self.test_page.save()

        self.test_job = Job(job_name="test job")
        self.test_job.save()

        self.test_workflowjob = WorkflowJob(job=self.test_job)
        self.test_workflowjob.save()

        self.test_workflow = Workflow(name="test workflow", project=self.test_project)
        self.test_workflow.save()

        self.test_workflowrun = WorkflowRun(workflow=self.test_workflow, creator=self.test_user)
        self.test_workflowrun.save()

    def test_save(self):
        test_runjob = RunJob(workflow_run=self.test_workflowrun, workflow_job=self.test_workflowjob, page=self.test_page)
        test_runjob.save()

        retr_runjob = RunJob.objects.get(page=self.test_page)
        self.assertEqual(retr_runjob, test_runjob)

    def test_delete(self):
        pass