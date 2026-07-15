from django.test import TestCase
# from rodan.models.job import Job
# from rodan.models.inputporttype import InputPortType
from model_bakery import baker
from rodan.test.helpers import RodanTestTearDownMixin, RodanTestSetUpMixin


class InputPortTypeTestCase(RodanTestTearDownMixin, TestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.test_job = baker.make("rodan.Job")
