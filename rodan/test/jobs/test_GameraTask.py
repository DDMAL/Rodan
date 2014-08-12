from django.test import TestCase
from celery import registry
from django.test.utils import override_settings
from rodan.jobs.gamera.celery_task import GameraTask
from rodan.models.resource import Resource


class to_greyscale_TestCase(TestCase):
    fixtures = ['1_users', '2_initial_data', '3_jobs']

    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       CELERY_ALWAYS_EAGER=True,
                       BROKER_BACKEND='memory')
    def test_GameraTask(self):
        task = GameraTask()
        task.name = "gamera.plugins.image_conversion.to_greyscale"
        registry.tasks.register(task)
        result = GameraTask.run_task(task, None, "3d558414db10427d82efdd9b9cb985bf")
        self.assertTrue(Resource.objects.get("{0}".format(result)).exists())
