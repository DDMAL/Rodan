from django.test import TestCase
from django.contrib.auth.models import User
from rodan.models import ResourceType, Resource
from model_mommy import mommy
from rodan.test.helpers import RodanTestTearDownMixin, RodanTestSetUpMixin


class ResourceTestCase(RodanTestTearDownMixin, TestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.test_user = mommy.make(User)
        self.test_output = mommy.make('rodan.Output')
        self.test_project = self.test_output.run_job.workflow_job.workflow.project
        self.test_inputport = mommy.make('rodan.InputPort',
                                         workflow_job=self.test_output.run_job.workflow_job)
        self.test_workflow = self.test_output.run_job.workflow_job.workflow

        self.test_resource_data = {
            "project": self.test_project,
            "creator": self.test_user,
            "name": "testresource.jpg",
            "resource_type": ResourceType.cached('test/a1')
        }


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
