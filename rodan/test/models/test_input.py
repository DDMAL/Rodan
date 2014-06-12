from django.test import TestCase
from rodan.models.inputport import InputPort
from rodan.models.runjob import RunJob
from rodan.models.resource import Resource
from rodan.models.input import Input


class InputTestCase(TestCase):
    fixtures = ['1_users', '2_initial_data']

    def setUp(self):
        self.test_runjob = RunJob.objects.get(uuid="3d558414db10427d82efdd9b9cb985bf")
        self.test_inputport = InputPort.objects.get(uuid="dd35645a7a7845c5a72c9a856ccb920e")
        self.test_resource = Resource.objects.get(uuid="e8c2672da2f04a54bf710f1a2212bb0e")

    def test_save(self):
        input = Input(input_port=self.test_inputport, resource=self.test_resource, run_job=self.test_runjob)
        input.save()

        retr_input = Input.objects.get(uuid=input.uuid)
        self.assertEqual(retr_input.resource, self.test_resource)

    def test_delete(self):
        input = Input(input_port=self.test_inputport, resource=self.test_resource, run_job=self.test_runjob)
        input.save()

        input.delete()

        retr_input = Input.objects.filter(resource=self.test_resource, input_port=self.test_inputport)
        self.assertFalse(retr_input.exists())
                
