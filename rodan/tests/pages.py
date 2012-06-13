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

        self.assertEqual(self.page_2.get_next_job(), None)

        # When you pass in the RodanUser with ID 1, should return Binarise
        user = RodanUser.objects.get(pk=1)
        self.assertEqual(self.page_2.get_next_job(user=user), self.binarise)

        # Now let's make that first result done, we should get rotation
        self.result_1.update_end_manual_time()
        self.result_1.update_end_total_time()

        self.assertEqual(self.page_2.get_next_job(user=user), self.rotate)
        self.assertEqual(self.page_2.get_next_job(), self.rotate)

        # Now let's pretend to start the rotate job
        new_result = Result.objects.create(page=self.page_2, \
                        job_item=JobItem.objects.get(pk=4), user=user)
        self.assertEqual(self.page_2.get_next_job(user=user), self.rotate)
        self.assertEqual(self.page_2.get_next_job(), None)

        # When we finish the job ...
        new_result.update_end_manual_time()
        new_result.update_end_total_time()
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
        self.assertTrue(self.page_2.get_latest_image_path().endswith("another.tiff"))
        self.result_file_1 = ResultFile.objects.create(result=self.result_1, \
                                result_type='tiff', filename='binarised.tiff')

        # Should return the original filename
        self.assertTrue(self.page_1.get_latest_image_path().endswith('lol.tiff'))
        self.assertEqual(self.page_1.get_latest_file_path('mei'), None)
        self.assertTrue(self.page_2.get_latest_image_path().endswith("binarised.tiff"))

        self.result_file_2 = ResultFile.objects.create(result=self.result_2, \
                                result_type='tiff', filename='recent.tiff')

        self.assertTrue(self.page_2.get_latest_image_path().endswith('recent.tiff'))

    def tearDown(self):
        self.result_1.end_total_time = None
        self.result_1.save()

        self.result_2.delete()
        self.result_file_1.delete()
        self.result_file_2.delete()
        
class GetThumbnailsToImage(unittest.TestCase):
    def setUp(self):
        self.result = Result.objects.get(pk=1)
        self.page = self.result.page
        self.job = self.result.job_item.job
    
    def runTest(self):
        self.assertTrue(self.page.get_thumb_path(size=100, job=None).endswith("another_100.jpg"))
    
    def tearDown(self):
        self.result.delete()

class PageTest(unittest.TestCase):
    def setUp(self):
        self.page_1 = Page.objects.get(pk=1)

    def testGetFilenameForJob(self):
        rotate_job = Job.objects.get(slug='rotate')
        root = rodan.settings.MEDIA_ROOT
        path = os.path.join(root, "1", "1", "rotate", "lol.tif")
        self.assertEqual(path, self.page_1.get_job_path(rotate_job, 'tif'))
