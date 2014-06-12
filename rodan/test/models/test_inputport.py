from django.test import TestCase
from rodan.models.workflowjob import WorkflowJob
from rodan.models.inputporttype import InputPortType
from rodan.models.inputport import InputPort


class InputPortTestCase(TestCase):
    fixtures = ['1_users', '2_initial_data']

    def setUp(self):
        self.test_workflowjob = WorkflowJob.objects.get(uuid="a21f510a16c24701ac0e435b3f4c20f3")
        self.test_inputporttype = InputPortType.objects.get(uuid="30ed42546fe440a181f64a2ebdea82e1")

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
