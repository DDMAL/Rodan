from django.test import TestCase
from rodan.models.workflowjob import WorkflowJob
from rodan.models.inputporttype import InputPortType
from rodan.models.inputport import InputPort
from model_mommy import mommy
from rodan.test.helpers import RodanTestTearDownMixin, RodanTestSetUpMixin

class InputPortTestCase(RodanTestTearDownMixin, TestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.test_workflowjob = mommy.make('rodan.WorkflowJob')
        self.test_inputporttype = mommy.make('rodan.InputPortType',
                                             job=self.test_workflowjob.job)

    def test_save(self):
        inputport = InputPort(label="test input port", input_port_type=self.test_inputporttype, workflow_job=self.test_workflowjob)
        inputport.save()

        retr_ip = InputPort.objects.get(label="test input port")
        self.assertEqual(retr_ip.label, "test input port")

    def test_save_default_label(self):
        inputport = InputPort(input_port_type=self.test_inputporttype, workflow_job=self.test_workflowjob)
        inputport.save()

        retr_ip = InputPort.objects.get(uuid=inputport.uuid)
        self.assertEqual(retr_ip.label, self.test_inputporttype.name)

    def test_delete(self):
        inputport = InputPort(label="test input port", input_port_type=self.test_inputporttype, workflow_job=self.test_workflowjob)
        inputport.save()

        inputport.delete()

        retr_ip = InputPort.objects.filter(label="test input port")
        self.assertFalse(retr_ip.exists())
