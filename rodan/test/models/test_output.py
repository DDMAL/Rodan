from django.test import TestCase
from rodan.models.resource import Resource
from rodan.models.outputport import OutputPort
from rodan.models.runjob import RunJob
from rodan.models.output import Output
from model_mommy import mommy
from rodan.test.helpers import RodanTestTearDownMixin


class OutputTestCase(RodanTestTearDownMixin, TestCase):
    def setUp(self):
        self.test_runjob = mommy.make('rodan.RunJob')
        self.test_outputport = mommy.make('rodan.OutputPort',
                                         output_port_type__job=self.test_runjob.workflow_job.job)
        self.test_resource = mommy.make('rodan.Resource',
                                        project=self.test_runjob.workflow_job.workflow.project)

    def test_save(self):
        output = Output(output_port=self.test_outputport, run_job=self.test_runjob, resource=self.test_resource)
        output.save()

        retr_output = Output.objects.get(resource=self.test_resource)
        self.assertEqual(retr_output.output_port, self.test_outputport)
