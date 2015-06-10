from django.test import TestCase
from rodan.models.job import Job
from model_mommy import mommy
from rodan.test.helpers import RodanTestTearDownMixin, RodanTestSetUpMixin


class JobTestCase(RodanTestTearDownMixin, TestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()

    def test_save(self):
        job = Job(name="test job")
        job.save()

        retr_job = Job.objects.get(name="test job")
        self.assertEqual(retr_job.name, job.name)

    def test_delete(self):
        job = Job(name="test job")
        job.save()

        retr_job = Job.objects.get(name="test job")
        retr_job.delete()

        retr_job2 = Job.objects.filter(name="test job")
        self.assertFalse(retr_job2.exists())
