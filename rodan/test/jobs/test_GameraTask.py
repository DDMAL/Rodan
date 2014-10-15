from PIL import Image
from rest_framework.test import APITestCase
from rodan.jobs.gamera.celery_task import GameraTask
from rodan.models.resource import Resource
from StringIO import StringIO
from model_mommy import mommy
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin


class GameraTaskTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_user()
        self.client.login(username="ahankins", password="hahaha")
        file_obj = StringIO()
        image = Image.new("RGBA", size=(50, 50), color=(256, 0, 0))
        image.save(file_obj, 'png')
        file_obj.name = 'page1.png'
        file_obj.seek(0)
        self.test_project = mommy.make('rodan.Project')
        resource_obj = {
            'project': "http://localhost:8000/project/{0}/".format(self.test_project.uuid),
            'files': [
                file_obj
            ],
        }
        retr_res = self.client.post("/resources/", resource_obj, format='multipart')
        self.test_resource = Resource.objects.get(pk=retr_res.data['resources'][0]['uuid'])
        self.test_output = mommy.make('rodan.Output',
                                      resource=self.test_resource)
        self.test_input = mommy.make('rodan.Input',
                                     resource=self.test_resource)
        self.test_resource.origin = self.test_output
        self.test_resource.save()
        self.test_workflowjob = mommy.make('rodan.WorkflowJob')
        self.test_workflowrun = mommy.make('rodan.WorkflowRun',
                                           workflow=self.test_workflowjob.workflow)
        self.test_runjob = mommy.make('rodan.RunJob',
                                      workflow_job=self.test_workflowjob,
                                      workflow_run=self.test_workflowrun)
        self.test_output.run_job = self.test_runjob
        self.test_output.save()
        self.test_input.run_job = self.test_runjob
        self.test_input.save()

    def test_to_greyscale_no_previous_result(self):
        task = GameraTask()
        task.name = "gamera.plugins.image_conversion.to_greyscale"
        result = task.run_task(output_id=None, runjob_id=self.test_runjob.uuid)

        result_image = Resource.objects.get(pk="{0}".format(result))
        im = Image.open(result_image.resource_file.path)
        self.assertEqual(im.mode, 'L')

    def test_to_greyscale(self):
        task = GameraTask()
        task.name = "gamera.plugins.image_conversion.to_greyscale"
        result = task.run_task(output_id=self.test_output.uuid, runjob_id=self.test_runjob.uuid)
        result_image = Resource.objects.get(pk="{0}".format(result))
        im = Image.open(result_image.resource_file.path)
        self.assertEqual(im.mode, 'L')

    def test_to_greyscale_incompatible_type(self):
        task = GameraTask()
        task.name = "gamera.plugins.binarization.niblack_threshold"
        self.assertRaises(TypeError, GameraTask.run, task, None, self.test_runjob.uuid)
