from django.test import TestCase
from rodan.models.inputport import InputPort
from rodan.models.runjob import RunJob
from rodan.models.resource import Resource
from rodan.models.input import Input
from model_mommy import mommy
from rodan.test.helpers import RodanTestTearDownMixin, RodanTestSetUpMixin


class InputTestCase(RodanTestTearDownMixin, TestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.test_runjob = mommy.make('rodan.RunJob')
        self.test_inputport = mommy.make('rodan.InputPort')
        self.test_resource = mommy.make('rodan.Resource')

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
