from django.test import TestCase
# from model_bakery import baker
from rodan.test.helpers import RodanTestTearDownMixin, RodanTestSetUpMixin


class WorkflowJobTestCase(RodanTestTearDownMixin, TestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()

    def test_save(self):
        pass
