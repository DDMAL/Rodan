import os, tempfile, shutil
from PIL import Image
from rest_framework.test import APITestCase
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
from celery import registry

import rodan.jobs.gamera  # register jobs into Celery registry

class GameraTaskTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()

        self.infile = self.new_temppath()
        self.outfile = self.new_temppath()
        self.inputs = {"Input Type #0": [{'resource_path': self.infile, 'resource_type': 'image/rgb+png'}]}
        self.outputs = {"Input Type #0": [{'resource_path': self.outfile, 'resource_type': 'image/rgb+png'}]}
        image = Image.new("RGBA", size=(50, 50), color=(256, 0, 0))
        image.save(self.infile, 'png')

    def test_to_greyscale_no_previous_result(self):
        task = registry.tasks["gamera.plugins.image_conversion.to_greyscale"]
        result = task.run_my_task(self.inputs, [], self.outputs)
        im = Image.open(self.outfile)
        self.assertEqual(im.mode, 'L')

    def test_to_greyscale(self):
        task = registry.tasks["gamera.plugins.image_conversion.to_greyscale"]
        result = task.run_my_task(self.inputs, [], self.outputs)
        im = Image.open(self.outfile)
        self.assertEqual(im.mode, 'L')

    def test_to_greyscale_incompatible_type(self):
        task = registry.tasks["gamera.plugins.binarization.niblack_threshold"]
        self.assertRaises(TypeError, task.run_my_task, self.inputs, [], self.outputs)
