from django.test import TestCase
# from rodan.models.resource import Resource
# from rodan.models.outputport import OutputPort
# from rodan.models.runjob import RunJob
from rodan.models.output import Output
from model_mommy import mommy
from rodan.test.helpers import RodanTestTearDownMixin, RodanTestSetUpMixin


class OutputTestCase(RodanTestTearDownMixin, TestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.test_runjob = mommy.make("rodan.RunJob")
        self.test_outputport = mommy.make("rodan.OutputPort")
        self.test_resource = mommy.make("rodan.Resource")

    def test_save(self):
        output = Output(
            output_port=self.test_outputport,
            run_job=self.test_runjob,
            resource=self.test_resource,
        )
        output.save()

        retr_output = Output.objects.get(resource=self.test_resource)
        self.assertEqual(retr_output.output_port, self.test_outputport)
