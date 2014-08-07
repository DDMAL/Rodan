from django.test import TestCase
from rodan.models.job import Job
from rodan.models.outputporttype import OutputPortType
from rodan.settings import IMAGE_TYPES


class OutputPortTypeTestCase(TestCase):
    fixtures = ['1_users', '2_initial_data']

    def setUp(self):
        self.test_job = Job.objects.get(uuid="76753dd66e1147bcbd6321d749518da2")

    def test_resource_type(self):
        output_port_type = OutputPortType(job=self.test_job,
                                          name="test output port type",
                                          resource_type=[IMAGE_TYPES[1], IMAGE_TYPES[3], IMAGE_TYPES[5]],
                                          minimum=1,
                                          maximum=1)
        output_port_type.save()

        retr_opt = OutputPortType.objects.get(name="test output port type")
        for type in retr_opt.resource_type:
            self.assertTrue(type in IMAGE_TYPES)

    def test_delete(self):
        output_port_type = OutputPortType(job=self.test_job, name="test output port type", resource_type=1, minimum=1, maximum=1)
        output_port_type.save()

        output_port_type.delete()

        retr_opt = OutputPortType.objects.filter(name="test output port type")
        self.assertFalse(retr_opt.exists())
