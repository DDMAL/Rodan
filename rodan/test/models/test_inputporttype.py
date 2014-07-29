from django.test import TestCase
from rodan.models.job import Job
from rodan.models.inputporttype import InputPortType
from mimetypes import types_map


class InputPortTypeTestCase(TestCase):
    fixtures = ['1_users', '2_initial_data']

    def setUp(self):
        self.test_job = Job.objects.get(uuid="76753dd66e1147bcbd6321d749518da2")

    def test_resource_type(self):
        input_port_type = InputPortType(job=self.test_job,
                                        name="test input port type",
                                        resource_type='application/xml',
                                        minimum=1,
                                        maximum=1)
        input_port_type.save()

        retr_ipt = InputPortType.objects.get(name="test input port type")
        self.assertTrue(retr_ipt.resource_type in types_map.values())

    def test_delete(self):
        input_port_type = InputPortType(job=self.test_job, name="test input port type", resource_type=0, minimum=1, maximum=1)
        input_port_type.save()

        input_port_type.delete()

        retr_ipt = InputPortType.objects.filter(name="test input port type")
        self.assertFalse(retr_ipt.exists())
