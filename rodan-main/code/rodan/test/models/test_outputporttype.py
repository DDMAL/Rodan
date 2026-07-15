from django.test import TestCase
# from rodan.models.job import Job
# from rodan.models.outputporttype import OutputPortType
from model_bakery import baker
from rodan.test.helpers import RodanTestTearDownMixin, RodanTestSetUpMixin


class OutputPortTypeTestCase(RodanTestTearDownMixin, TestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.test_job = baker.make("rodan.Job")
