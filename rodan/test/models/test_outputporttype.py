from django.test import TestCase
from rodan.models.job import Job
from rodan.models.outputporttype import OutputPortType
from model_mommy import mommy
from rodan.test.helpers import RodanTestTearDownMixin, RodanTestSetUpMixin

class OutputPortTypeTestCase(RodanTestTearDownMixin, TestCase, RodanTestSetUpMixin):

    def setUp(self):
        self.setUp_rodan()
        self.test_job = mommy.make('rodan.Job')

    def test_delete(self):
        output_port_type = OutputPortType(job=self.test_job, name="test output port type", minimum=1, maximum=1)
        output_port_type.save()

        output_port_type.delete()

        retr_opt = OutputPortType.objects.filter(name="test output port type")
        self.assertFalse(retr_opt.exists())
