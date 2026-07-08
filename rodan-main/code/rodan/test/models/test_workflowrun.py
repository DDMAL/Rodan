from django.test import TestCase
from rodan.models import WorkflowRun, User
from model_bakery import baker
from rodan.test.helpers import RodanTestTearDownMixin, RodanTestSetUpMixin


class WorkflowRunTestCase(RodanTestTearDownMixin, TestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.test_user = baker.make(User)
        self.test_project = baker.make("rodan.Project")
        self.test_workflow = baker.make("rodan.Workflow")
        self.test_resource = baker.make("rodan.resource")

        self.test_workflowrun_data = {
            "name": "test workflowrun",
            "project": self.test_project,
            "creator": self.test_user,
        }

    def test_delete(self):
        workflowrun = WorkflowRun(**self.test_workflowrun_data)
        workflowrun.save()

        retr_workflowrun = WorkflowRun.objects.filter(name="testworkflowrun.jpg")
        retr_workflowrun.delete()

        retr_workflowrun2 = WorkflowRun.objects.filter(name="testworkflowrun.jpg")
        self.assertFalse(retr_workflowrun2.exists())
