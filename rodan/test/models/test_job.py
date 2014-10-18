from django.test import TestCase
from rodan.models.job import Job
from model_mommy import mommy
from rodan.test.helpers import RodanTestTearDownMixin, RodanTestSetUpMixin


class JobTestCase(RodanTestTearDownMixin, TestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()

    def test_save(self):
        job = Job(job_name="test job")
        job.save()

        retr_job = Job.objects.get(job_name="test job")
        self.assertEqual(retr_job.job_name, job.job_name)

    def test_delete(self):
        job = Job(job_name="test job")
        job.save()

        retr_job = Job.objects.get(job_name="test job")
        retr_job.delete()

        retr_job2 = Job.objects.filter(job_name="test job")
        self.assertFalse(retr_job2.exists())
