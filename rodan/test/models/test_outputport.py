from django.test import TestCase
from rodan.models.workflowjob import WorkflowJob
from rodan.models.outputporttype import OutputPortType
from rodan.models.outputport import OutputPort
from model_mommy import mommy
from rodan.test.helpers import RodanTestTearDownMixin


class OutputPortTestCase(RodanTestTearDownMixin, TestCase):
    def setUp(self):
        self.test_workflowjob = mommy.make('rodan.WorkflowJob')
        self.test_outputporttype = mommy.make('rodan.OutputPortType',
                                              job=self.test_workflowjob.job)

    def test_save(self):
        outputport = OutputPort(label="test output port", output_port_type=self.test_outputporttype, workflow_job=self.test_workflowjob)
        outputport.save()

        retr_op = OutputPort.objects.get(label="test output port")
        self.assertEqual(retr_op.label, "test output port")

    def test_save_default_label(self):
        outputport = OutputPort(output_port_type=self.test_outputporttype, workflow_job=self.test_workflowjob)
        outputport.save()

        retr_op = OutputPort.objects.get(uuid=outputport.uuid)
        self.assertEqual(retr_op.label, self.test_outputporttype.name)
