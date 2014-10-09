from django.test import TestCase
from rodan.models.job import Job
from rodan.models.outputporttype import OutputPortType
from rodan.models.resource import ResourceType
from model_mommy import mommy
from rodan.test.helpers import RodanTestTearDownMixin

class OutputPortTypeTestCase(RodanTestTearDownMixin, TestCase):

    def setUp(self):
        self.test_job = mommy.make('rodan.Job')

    def test_resource_type(self):
        output_port_type = OutputPortType(job=self.test_job,
                                          name="test output port type",
                                          resource_type=[ResourceType.GREYSCALE, ResourceType.RGB, ResourceType.COMPLEX],
                                          minimum=1,
                                          maximum=1)
        output_port_type.save()

        retr_opt = OutputPortType.objects.get(name="test output port type")
        for type in retr_opt.resource_type:
            self.assertTrue(type in ResourceType.IMAGE_TYPES)

    def test_delete(self):
        output_port_type = OutputPortType(job=self.test_job, name="test output port type", resource_type=1, minimum=1, maximum=1)
        output_port_type.save()

        output_port_type.delete()

        retr_opt = OutputPortType.objects.filter(name="test output port type")
        self.assertFalse(retr_opt.exists())
