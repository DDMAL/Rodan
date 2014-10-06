from PIL import Image
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rodan.jobs.gamera.celery_task import GameraTask
from rodan.models.resource import Resource
from model_mommy import mommy


class GameraTaskTestCase(APITestCase):
    fixtures = ['1_users', '3_jobs']

    def setUp(self):
        self.client.login(username="ahankins", password="hahaha")
        self.test_project = mommy.make('rodan.Project')
        resource_obj = {
            'project': "http://localhost:8000/project/{0}/".format(self.test_project.uuid),
            'files': [
                SimpleUploadedFile('page1.png', 'n/t')
            ],
        }
        retr_res = self.client.post("/resources/", resource_obj, format='multipart').data['resources']
        self.test_resource = Resource.objects.get(pk=retr_res[0]['uuid'])
        self.test_output = mommy.make('rodan.Output',
                                      resource=self.test_resource)
        self.test_workflowjob = mommy.make('rodan.WorkflowJob')
        self.test_workflowrun = mommy.make('rodan.WorkflowRun',
                                           workflow=self.test_workflowjob.workflow)
        self.test_runjob = mommy.make('rodan.RunJob',
                                      workflow_job=self.test_workflowjob,
                                      workflow_run=self.test_workflowrun)

    def test_to_greyscale_no_previous_result(self):
        task = GameraTask()
        task.name = "gamera.plugins.image_conversion.to_greyscale"
        #def run_task(self, output_id, runjob_id, *args, **kwargs)
        result = task.run_task(None, self.test_runjob.uuid)

        result_image = Resource.objects.get(pk="{0}".format(result))
        im = Image.open(result_image.resource_file.path)
        self.assertEqual(im.mode, 'L')

    def test_to_greyscale(self):
        task = GameraTask()
        task.name = "gamera.plugins.image_conversion.to_greyscale"
        result = task.run_task(self.test_output.uuid, self.test_runjob.uuid)
        result_image = Resource.objects.get(pk="{0}".format(result))
        im = Image.open(result_image.resource_file.path)
        self.assertEqual(im.mode, 'L')

    def test_to_greyscale_incompatible_type(self):
        task = GameraTask()
        task.name = "gamera.plugins.binarization.niblack_threshold"
        self.assertRaises(TypeError, GameraTask.run, task, None, self.test_runjob.uuid)
