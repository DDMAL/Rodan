import os, tempfile, shutil, uuid, types
from celery import registry
from django.conf import settings
from rest_framework.test import APITestCase
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
from rodan.jobs.base import RodanTask
import rodan.jobs.load   # load all jobs before adding methods for the TestCase class.

class RodanJobsTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()

    def new_available_path(self):
        "This method will only return an available file path, not creating the file! But it creates the parent directory."
        try:
            os.makedirs(settings.MEDIA_ROOT)
        except OSError:
            pass
        return os.path.join(settings.MEDIA_ROOT, str(uuid.uuid1()))

# dynamically add test methods for all jobs
def wrapper_fn(task):
    return lambda testcase: task.test_my_task(testcase)
for task in registry.tasks.values():
    if isinstance(task, RodanTask):
        setattr(RodanJobsTestCase, 'test::{0}'.format(task.name), wrapper_fn(task))
