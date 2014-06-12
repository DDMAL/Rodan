from django.test import TestCase
from rodan.models.resource import Resource
from rodan.models.outputport import OutputPort
from rodan.models.runjob import RunJob
from rodan.models.output import Output


class OutputTestCase(TestCase):
    fixtures = ['1_users', '2_initial_data']

    def setUp(self):
        self.test_resource = Resource.objects.get(uuid="e8c2672da2f04a54bf710f1a2212bb0e")
        self.test_outputport = OutputPort.objects.get(uuid="bbdd13ddf05844aa8549e93e82ae4fd2")
        self.test_runjob = RunJob.objects.get(uuid="3d558414db10427d82efdd9b9cb985bf")

    def test_save(self):
        output = Output(output_port=self.test_outputport, run_job=self.test_runjob, resource=self.test_resource)
        output.save()

        retr_output = Output.objects.get(resource=self.test_resource)
        self.assertEqual(retr_output.output_port, self.test_outputport)
