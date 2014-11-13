import os, tempfile, shutil
from PIL import Image
from rest_framework.test import APITestCase
from rodan.models.resource import Resource
from StringIO import StringIO
from model_mommy import mommy
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin


class GameraTaskTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.client.login(username="ahankins", password="hahaha")

        self._tmpdir = tempfile.mkdtemp()
        self.infile = os.path.join(self._tmpdir, 'in')
        self.outfile = os.path.join(self._tmpdir, 'out')
        self.inputs = {"Input Type #0": [{'resource_path': self.infile, 'resource_type': 'image/rgb+png'}]}
        self.outputs = {"Input Type #0": [{'resource_path': self.outfile, 'resource_type': 'image/rgb+png'}]}
        image = Image.new("RGBA", size=(50, 50), color=(256, 0, 0))
        image.save(self.infile, 'png')

        from rodan.jobs.gamera.celery_task import GameraTask
        self.task = GameraTask()

    def test_to_greyscale_no_previous_result(self):
        self.task.name = "gamera.plugins.image_conversion.to_greyscale"
        result = self.task.run_my_task(self.inputs, [], self.outputs)
        im = Image.open(self.outfile)
        self.assertEqual(im.mode, 'L')

    def test_to_greyscale(self):
        self.task.name = "gamera.plugins.image_conversion.to_greyscale"
        result = self.task.run_my_task(self.inputs, [], self.outputs)
        im = Image.open(self.outfile)
        self.assertEqual(im.mode, 'L')

    def test_to_greyscale_incompatible_type(self):
        self.task.name = "gamera.plugins.binarization.niblack_threshold"
        self.assertRaises(TypeError, self.task.run_my_task, self.inputs, [], self.outputs)

    def tearDown(self):
        super(GameraTaskTestCase, self).tearDown()
        shutil.rmtree(self._tmpdir)
