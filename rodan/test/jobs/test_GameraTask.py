from django.test import TestCase
from celery import registry
from django.test.utils import override_settings
from rodan.jobs.gamera.celery_task import GameraTask
from rodan.models.resource import Resource


class GameraTaskTestCase(TestCase):
    fixtures = ['1_users', '2_initial_data', '3_jobs']

    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       CELERY_ALWAYS_EAGER=True,
                       BROKER_BACKEND='memory')
    def test_to_greyscale_no_previous_result(self):
        task = GameraTask()
        task.name = "gamera.plugins.image_conversion.to_greyscale"
        registry.tasks.register(task)
        result = GameraTask.run_task(task, None, "3d558414db10427d82efdd9b9cb985bf")
        self.assertTrue(Resource.objects.filter(pk="{0}".format(result)).count())

    def test_to_greyscale(self):
        task = GameraTask()
        task.name = "gamera.plugins.image_conversion.to_greyscale"
        result = GameraTask.run_task(task, "e8c2672da2f04a54bf710f1a2212bb0e", "3d558414db10427d82efdd9b9cb985bf")
        self.assertTrue(Resource.objects.get("{0}".format(result)).exists())
