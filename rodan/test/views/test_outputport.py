from rest_framework.test import APITestCase
from rest_framework import status
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin


class OutputPortViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_basic_workflow()
        self.client.login(username="ahankins", password="hahaha")

    def test_post(self):
        op_obj = {
            'workflow_job': "http://localhost:8000/workflowjob/{0}/".format(self.test_workflowjob.uuid),
            'output_port_type': "http://localhost:8000/outputporttype/{0}/".format(self.test_outputporttype.uuid),
        }

        response = self.client.post("/outputports/", op_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
