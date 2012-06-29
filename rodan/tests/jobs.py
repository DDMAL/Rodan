from django.utils import unittest

from rodan.models.projects import Job, JobItem, RodanUser, Workflow, Page
from rodan.models.results import Result
from rodan.jobs.diva import diva


class TestTyping(unittest.TestCase):
    def setUp(self):
        self.binarise = Job.objects.get(slug='simple-binarise')
        self.rotate = Job.objects.get(slug='rotate')

    def runTest(self):
        # A simple test for now, until the real types are set up
        self.assertFalse(self.rotate in self.binarise.get_compatible_jobs())
        self.assertTrue(self.binarise in self.rotate.get_compatible_jobs())


class TestDiva(unittest.TestCase):
    def test_stuff(self):
        job = Job.objects.get(pk='diva-preprocess')
        job_item = JobItem.objects.get(workflow=Workflow.objects.get(pk=1), job=job)
        page = Page.objects.get(pk=2)
        result = Result.objects.create(job_item=job_item, user=RodanUser.objects.get(pk=1), page=page)
        diva.delay(result.id, compression='jpeg', quality=75, tile_size=256)

        # Check that the pyramidal tiff file has been created
        output_path = page.get_pyramidal_tiff_path()
        try:
            open(output_path)
        except IOError:
            self.fail("File does not exist!!!!!! AHHHHH")
