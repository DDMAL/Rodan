import os

from django.utils import unittest, timezone

from rodan.models.projects import Project, Job, Page, JobItem, RodanUser
from rodan.models.results import Result, ResultFile
from rodan.models.jobs import JobType
import rodan.settings


class GetNextJob(unittest.TestCase):
    def setUp(self):
        self.page_1 = Page.objects.get(pk=1)
        self.page_2 = Page.objects.get(pk=2)
        self.crop = Job.objects.get(name="Crop")
        self.rotate = Job.objects.get(name="Rotate")
        self.binarise = Job.objects.get(name="Binarise (simple threshold)")
        self.result_1 = Result.objects.get(pk=1)

    def runTest(self):
        """Just the fixtures, no changes
        """
        self.assertEqual(self.page_1.get_next_job(), self.crop)

        self.assertEqual(self.page_2.get_next_job(), self.rotate)

        # When you pass in the RodanUser with ID 1, should return Binarise
        user = RodanUser.objects.get(pk=1)
        self.assertEqual(self.page_2.get_next_job(user=user), self.binarise)

        # Now let's make that first result done, we should get rotation
        self.result_1.end_total_time = timezone.now()
        self.result_1.save()

        self.assertEqual(self.page_2.get_next_job(user=user), self.rotate)
        self.assertEqual(self.page_2.get_next_job(), self.rotate)

        # Now let's pretend to start the rotate job
        new_result = Result.objects.create(page=self.page_2, \
                        job_item=JobItem.objects.get(pk=4), user=user)
        self.assertEqual(self.page_2.get_next_job(user=user), self.rotate)
        self.assertEqual(self.page_2.get_next_job(), self.crop)

    def tearDown(self):
        # Clear the end_total_time thing for the result
        self.result_1.end_total_time = None
        self.result_1.save()

        # Delete the result we created
        Result.objects.get(pk=2).delete()


class GetLatestImagePath(unittest.TestCase):
    def setUp(self):
        self.result_1 = Result.objects.get(pk=1)
        self.result_1.end_total_time = timezone.now()
        self.result_1.save()
        self.page_1 = Page.objects.get(pk=1)
        self.page_2 = Page.objects.get(pk=2)
        self.user = RodanUser.objects.get(pk=1)

        # A result for the rotate job
        self.result_2 = Result.objects.create(job_item = JobItem.objects.get(pk=4), \
                                user=self.user, page=self.page_2, end_total_time=timezone.now())

    def runTest(self):
        self.assertTrue(self.page_2.get_latest_file(JobType.IMAGE).endswith("another.tif"))
        self.result_file_1 = ResultFile.objects.create(result=self.result_1, \
                                result_type=JobType.IMAGE_ONEBIT, filename='binarised.tif')

        # Should return the original filename
        self.assertTrue(self.page_1.get_latest_file(JobType.IMAGE).endswith('lol.tif'))
        self.assertEqual(self.page_1.get_latest_file(JobType.MEI), None)
        self.assertTrue(self.page_2.get_latest_file(JobType.IMAGE).endswith("binarised.tif"))

        self.result_file_2 = ResultFile.objects.create(result=self.result_2, \
                                result_type=JobType.IMAGE_ONEBIT, filename='recent.tif')

        self.assertTrue(self.page_2.get_latest_file(JobType.IMAGE).endswith('recent.tif'))

    def tearDown(self):
        self.result_1.end_total_time = None
        self.result_1.save()

        self.result_2.delete()
        self.result_file_1.delete()
        self.result_file_2.delete()

class PageTest(unittest.TestCase):
    def setUp(self):
        self.page_1 = Page.objects.get(pk=1)

    def testGetFilenameForJob(self):
        root = rodan.settings.MEDIA_ROOT
        path = os.path.join(root, "1", "1", "2", "lol.tif")
        self.assertEqual(path, self.page_1.get_filename_for_job(2))
