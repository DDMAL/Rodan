from PIL import Image
from django.test import TestCase
from celery import registry
from rodan.jobs.gamera.celery_task import GameraTask
from rodan.models.resource import Resource


class GameraTaskTestCase(TestCase):
    fixtures = ['1_users', '2_initial_data', '3_jobs']

    def test_to_greyscale_no_previous_result(self):
        task = GameraTask()
        task.name = "gamera.plugins.image_conversion.to_greyscale"
        registry.tasks.register(task)
        result = GameraTask.run(task, None, "3d558414db10427d82efdd9b9cb985bf")

        result_image = Resource.objects.get(pk="{0}".format(result))
        im = Image.open(result_image.resource_file.path)
        self.assertEqual(im.mode, 'L')

    def test_to_greyscale(self):
        task = GameraTask()
        task.name = "gamera.plugins.image_conversion.to_greyscale"
        result = GameraTask.run(task, "04ae88f664664d3eaa68406c7c2f1211", "3d558414db10427d82efdd9b9cb985bf")
        result_image = Resource.objects.get(pk="{0}".format(result))
        im = Image.open(result_image.resource_file.path)
        self.assertEqual(im.mode, 'L')

    def test_to_greyscale_incompatible_type(self):
        task = GameraTask()
        task.name = "gamera.plugins.binarization.niblack_threshold"
        self.assertRaises(TypeError, GameraTask.run, task, None, "3d558414db10427d82efdd9b9cb985bf")
