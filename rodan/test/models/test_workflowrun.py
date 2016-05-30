from django.test import TestCase
from django.contrib.auth.models import User
from rodan.models import WorkflowRun
from model_mommy import mommy
from rodan.test.helpers import RodanTestTearDownMixin, RodanTestSetUpMixin


class WorkflowRunTestCase(RodanTestTearDownMixin, TestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.test_user = mommy.make(User)
        self.test_project = mommy.make('rodan.Project')
        self.test_workflow = mommy.make('rodan.Workflow')
        self.test_resource = mommy.make('rodan.resource')

        self.test_workflowrun_data = {
            "name": "test workflowrun",
            "project": self.test_project,
            "creator": self.test_user
        }

    def test_delete(self):
        workflowrun = WorkflowRun(**self.test_workflowrun_data)
        workflowrun.save()

        retr_workflowrun = WorkflowRun.objects.filter(name="testworkflowrun.jpg")
        retr_workflowrun.delete()

        retr_workflowrun2 = WorkflowRun.objects.filter(name="testworkflowrun.jpg")
        self.assertFalse(retr_workflowrun2.exists())

