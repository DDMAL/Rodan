from django.test import TestCase
from django.contrib.auth.models import User
from rodan.models.resource import Resource
from rodan.models.project import Project
from rodan.models.output import Output
from rodan.models.inputport import InputPort
from rodan.models.workflow import Workflow


class ResourceTestCase(TestCase):
    fixtures = ["1_users", "2_initial_data"]

    def setUp(self):
        self.test_user = User.objects.get(username="ahankins")
        self.test_project = Project.objects.get(uuid="9e8e928b4ec24a09b6113f1b0af1ea53")
        self.test_output = Output.objects.get(uuid="04ae88f664664d3eaa68406c7c2f1211")
        self.test_inputport = InputPort.objects.get(uuid="e38b11918691486cbd99627e5baec0a1")
        self.test_workflow = Workflow.objects.get(uuid="df78a1aa79554abcb5f1b0ac7bba2bad")

        self.test_resource_data = {
            "project": self.test_project,
            "creator": self.test_user,
            "name": "testresource.jpg",
        }

    def test_save_original_file(self):
        resource = Resource(**self.test_resource_data)
        resource.save()

        retr_resource = Resource.objects.get(name="testresource.jpg")
        self.assertEqual(retr_resource.resource_type, "image/jpeg")
        self.assertEqual(retr_resource.name, resource.name)

    def test_save_runjob_result(self):
        resource = Resource(**self.test_resource_data)
        resource.save()

        retr_resource = Resource.objects.get(name="testresource.jpg")
        self.assertEqual(retr_resource.name, resource.name)

    def test_delete(self):
        resource = Resource(**self.test_resource_data)
        resource.save()

        retr_resource = Resource.objects.get(name="testresource.jpg")
        retr_resource.delete()

        retr_resource2 = Resource.objects.filter(name="testresource.jpg")
        self.assertFalse(retr_resource2.exists())
