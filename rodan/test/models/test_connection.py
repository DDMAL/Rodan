from django.test import TestCase
from rodan.models.inputport import InputPort
from rodan.models.workflowjob import WorkflowJob
from rodan.models.outputport import OutputPort
from rodan.models.job import Job
from rodan.models.connection import Connection
from model_mommy import mommy


class ConnectionTestCase(TestCase):
    def setUp(self):
        self.test_inputport = mommy.make('rodan.InputPort')
        self.workflow = self.test_inputport.workflow_job.workflow
        self.test_outputport = mommy.make('rodan.OutputPort',
                                          workflow_job__workflow=self.workflow)

    def test_save(self):
        connection = Connection(input_port=self.test_inputport,
                                output_port=self.test_outputport)
        connection.save()

        retr_conn = Connection.objects.get(uuid=connection.uuid)
        self.assertEqual(retr_conn.workflow, self.workflow)
