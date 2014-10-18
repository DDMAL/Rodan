from django.test import TestCase
from rodan.models.job import Job
from rodan.models.inputporttype import InputPortType
from model_mommy import mommy
from rodan.test.helpers import RodanTestTearDownMixin, RodanTestSetUpMixin


class InputPortTypeTestCase(RodanTestTearDownMixin, TestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.test_job = mommy.make('rodan.Job')

    def test_delete(self):
        input_port_type = InputPortType(job=self.test_job, name="test input port type", minimum=1, maximum=1)
        input_port_type.save()

        input_port_type.delete()

        retr_ipt = InputPortType.objects.filter(name="test input port type")
        self.assertFalse(retr_ipt.exists())
