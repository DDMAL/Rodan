import os, tempfile, shutil, uuid, types, traceback, sys
from celery import registry
from django.conf import settings
from rest_framework.test import APITestCase
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
from rodan.jobs.base import RodanTask
class RodanJobsTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
    def new_available_path(self):
        """This method will only return an available file path, not creating the
          file! But it creates the parent directory."""
        try:
            os.makedirs(settings.MEDIA_ROOT)
        except OSError:
            pass
        return os.path.join(settings.MEDIA_ROOT, str(uuid.uuid1()))
    def test_all_jobs(self):
        import rodan.jobs.load   # load all jobs
        rodan_tasks = []
        for task in registry.tasks.values():
            if isinstance(task, RodanTask):
                rodan_tasks.append(task)
        total = len(rodan_tasks)
        failed = []
        for i, task in enumerate(rodan_tasks):
            print("{0}/{1}: {2} ... ".format(i+1, total, task.name),)
            try:
                task.test_my_task(self)
            except Exception as e:
                print("FAILED")
                tb = traceback.format_exc()
                failed.append((f"{task.name} {task.__class__}", tb))
            else:
                print("p")
        if failed:
            failed_msg = ""
            for name, trace in failed:
                failed_msg += f"======================\n{name}\n======================\n{trace}"
            self.fail(f"{len(failed)} jobs out of {total} failed\n{failed_msg}")
            # self.fail("{0} job(s) out of {1} failed.\n\n{2}".format(
            #     len(failed),
            #     total,
            #     '\n\n'.join(
            #         map(lambda f: "{0}\n{1}".format(f[0], f[1]), failed)
            #     )
            # )