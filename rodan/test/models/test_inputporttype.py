from django.test import TestCase
from rodan.models.job import Job
from rodan.models.inputporttype import InputPortType
from model_mommy import mommy
from rodan.test.helpers import RodanTestTearDownMixin, RodanTestSetUpMixin


class InputPortTypeTestCase(RodanTestTearDownMixin, TestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.test_job = mommy.make("rodan.Job")
