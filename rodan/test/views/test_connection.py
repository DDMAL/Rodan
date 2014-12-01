from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rodan.models.connection import Connection
from rodan.models.workflowjob import WorkflowJob
from rodan.models.outputport import OutputPort
from rodan.models.inputport import InputPort
from rodan.models.inputporttype import InputPortType
from model_mommy import mommy
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
import uuid

class ConnectionViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_basic_workflow()
        self.client.login(username="ahankins", password="hahaha")

        self.test_inputport = mommy.make('rodan.InputPort', workflow_job=self.test_workflowjob2)
        self.test_outputport = self.test_workflowjob.output_ports.all()[0]

    def test_get_list(self):
        response = self.client.get("/connections/")
        response_connections = []
        for conn in response.data['results']:
            response_connections.append(Connection.objects.get(uuid=conn['uuid']))
        self.assertEqual(str(response_connections), str(Connection.objects.all()))

    def test_post(self):
        test_conn = Connection(input_port=self.test_inputport,
                               output_port=self.test_outputport)
        test_conn.save()

        conn_obj = {
            'input_port': "http://localhost:8000/inputport/{0}/".format(self.test_inputport.uuid),
            'input_workflow_job': "http://localhost:8000/workflowjob/{0}/".format(self.test_workflowjob2.uuid),
            'output_port': "http://localhost:8000/outputport/{0}/".format(self.test_outputport.uuid),
            'output_workflow_job': "http://localhost:8000/workflowjob/{0}/".format(self.test_workflowjob.uuid),
        }

        response = self.client.post("/connections/", conn_obj, format='json')
        retr_conn = Connection.objects.get(uuid=response.data["uuid"])
        self.assertEqual(self.test_workflowjob.workflow, retr_conn.workflow)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_no_inputport(self):
        conn_obj = {
            'output_port': "http://localhost:8000/outputport/{0}/".format(self.test_outputport.uuid)
        }

        response = self.client.post("/connections/", conn_obj, format='json')
        anticipated_message = {'input_port': ['This field is required.']}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_badly_formatted_inputport(self):
        conn_obj = {
            'input_port': "http://localhost:8000/inputport/{0}".format(self.test_inputport.uuid),
            'output_port': "http://localhost:8000/outputport/{0}/".format(self.test_outputport.uuid)
        }

        response = self.client.post("/connections/", conn_obj, format='json')
        anticipated_message = {'input_port': ['Invalid hyperlink - No URL match']}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_a_real_inputport(self):
        conn_obj = {
            'input_port': "http://localhost:8000/inputport/{0}/".format(uuid.uuid1().hex),
            'output_port': "http://localhost:8000/outputport/{0}/".format(self.test_outputport.uuid)
        }

        response = self.client.post("/connections/", conn_obj, format='json')
        anticipated_message = {'input_port': ['Invalid hyperlink - Object does not exist.']}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete(self):
        test_conn_uuid = self.test_outputport.connections.all()[0].uuid
        response = self.client.delete("/connection/{0}/.json".format(test_conn_uuid), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Connection.objects.filter(pk=test_conn_uuid))
