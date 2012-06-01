from django.utils import unittest, timezone
from rodan.models.projects import Project, Job, Page, JobItem, RodanUser
from rodan.models.results import Result, ResultFile
from rodan.models.jobs import JobType

class GetNextJob(unittest.TestCase):
    def setUp(self):
        self.page_1 = Page.objects.get(pk=1)
        self.page_2 = Page.objects.get(pk=2)
        self.crop = Job.objects.get(name="Crop")
        self.rotate = Job.objects.get(name="Awesome rotation")
        self.binarise = Job.objects.get(name="Binarise")
        self.result = Result.objects.get(pk=1)

    def runTest(self):
        """Just the fixtures, no changes
        """
        self.assertEqual(self.page_1.get_next_job(), self.crop)

        self.assertEqual(self.page_2.get_next_job(), self.rotate)

        # When you pass in the RodanUser with ID 1, should return Binarise
        user = RodanUser.objects.get(pk=1)
        self.assertEqual(self.page_2.get_next_job(user=user), self.binarise)

        # Now let's make that first result done, we should get rotation
        self.result.end_total_time = timezone.now()
        self.result.save()

        self.assertEqual(self.page_2.get_next_job(user=user), self.rotate)
        self.assertEqual(self.page_2.get_next_job(), self.rotate)

        # Now let's pretend to start the rotate job
        new_result = Result.objects.create(page=self.page_2, job_item=JobItem.objects.get(pk=4), user=user)
        self.assertEqual(self.page_2.get_next_job(user=user), self.rotate)
        self.assertEqual(self.page_2.get_next_job(), self.crop)

    def tearDown(self):
        # Clear the end_total_time thing for the result
        self.result.end_total_time = None
        self.result.save()

        # Delete the result we created
        Result.objects.get(pk=2).delete()

class GetLatestImagePath(unittest.TestCase):
    def setUp(self):
        self.result = Result.objects.get(pk=1)
        self.result.end_total_time = timezone.now()
        self.result.save()
        self.page_1 = Page.objects.get(pk=1)
        self.page_2 = Page.objects.get(pk=2)
        self.result_file = ResultFile.objects.create(result=self.result, result_type=JobType.IMAGE, filename='binarised.tif')

    def test_shit(self):
        # Should return the original filename
        self.assertEqual(self.page_1.get_latest_file(JobType.IMAGE), 'lol.tif')
        self.assertEqual(self.page_1.get_latest_file(JobType.OTHER), None)
        self.assertEqual(self.page_2.get_latest_file(JobType.IMAGE).filename, "binarised.tif")

    def tearDown(self):
        self.result.end_total_time = None
        self.result.save()
