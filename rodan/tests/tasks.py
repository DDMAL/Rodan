from django.utils import unittest
from rodan.models.projects import Page
from rodan.jobs import utility
import gamera.core


class TestTask(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gamera.core.init_gamera()
    
    def testGenerateThumbnails(self):
        page = Page.objects.get(pk=2)
        output_img = gamera.core.load_image(page.get_filename_for_job("rodan.jobs.binarisation.SimpleThresholdBinarise"))
        #utility.create_thumbnails(output_img, page)