from django.utils import unittest
from rodan.models.projects import Page
from rodan.jobs import utils
import gamera.core


class TestTask(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gamera.core.init_gamera()
    
    def testGenerateThumbnails(self):
        pass
