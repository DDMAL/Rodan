from django.test import TestCase
from django.contrib.auth.models import User
from rodan.models.workflow import Workflow
from rodan.models.project import Project


class WorkflowTestCase(TestCase):
    fixtures = ["1_users", "2_initial_data"]

    def setUp(self):
        self.test_user = User.objects.get(username="ahankins")
        self.test_project = Project.objects.get(uuid="9e8e928b4ec24a09b6113f1b0af1ea53")

    def test_save(self):
        workflow = Workflow.objects.create(name="test workflow", project=self.test_project, creator=self.test_user)
        workflow.save()

        retr_workflow = Workflow.objects.get(name="test workflow")
        self.assertEqual(retr_workflow.name, workflow.name)

    def test_delete(self):
        workflow = Workflow.objects.create(name="test workflow", project=self.test_project, creator=self.test_user)
        workflow.save()

        retr_workflow = Workflow.objects.get(name="test workflow")
        retr_workflow.delete()

        retr_workflow2 = Workflow.objects.filter(name="test workflow")
        self.assertFalse(retr_workflow2.exists())
