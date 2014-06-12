from django.test import TestCase
from rodan.models.workflowjob import WorkflowJob
from rodan.models.outputporttype import OutputPortType
from rodan.models.outputport import OutputPort


class OutputPortTestCase(TestCase):
    fixtures = ['1_users', '2_initial_data']

    def setUp(self):
        self.test_workflowjob = WorkflowJob.objects.get(uuid="a21f510a16c24701ac0e435b3f4c20f3")
        self.test_outputporttype = OutputPortType.objects.get(uuid="1cdb067e98194da48dd3dfa35e84671c")

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
