from django.test import TestCase
from django.contrib.auth.models import User
from rodan.models.resource import Resource
from rodan.models.project import Project
from rodan.models.runjob import RunJob


class ResourceTestCase(TestCase):
    fixtures = ["1_users", "2_initial_data"]

    def setUp(self):
        self.test_user = User.objects.get(username="ahankins")
        self.test_project = Project.objects.get(uuid="9e8e928b4ec24a09b6113f1b0af1ea53")
        self.test_runjob = RunJob.objects.get(uuid="3d558414db10427d82efdd9b9cb985bf")

    def test_save_original_file(self):
        resource = Resource(project=self.test_project, creator=self.test_user, name="test resource")
        resource.save()

        retr_resource = Resource.objects.get(name="test resource")
        self.assertEqual(retr_resource.name, resource.name)

    def test_save_runjob_result(self):
        resource = Resource(project=self.test_project, runjob=self.test_runjob, output="output1-1", name="test resource")
        resource.save()

        retr_resource = Resource.objects.get(name="test resource")
        self.assertEqual(retr_resource.name, resource.name)

    def test_save_no_output(self):
        resource = Resource(project=self.test_project, runjob=self.test_runjob, name="test resource")
        resource.save()

        retr_resource = Resource.objects.get(name="test resource")
        self.assertEqual(retr_resource.origin, None)

    def test_delete(self):
        resource = Resource(project=self.test_project, creator=self.test_user, name="test resource")
        resource.save()

        retr_resource = Resource.objects.get(name="test resource")
        retr_resource.delete()

        retr_resource2 = Resource.objects.filter(name="test resource")
        self.assertFalse(retr_resource2.exists())
