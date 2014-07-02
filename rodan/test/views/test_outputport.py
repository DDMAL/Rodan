from rest_framework.test import APITestCase
from rest_framework import status


class OutputPortViewTestCase(APITestCase):
    fixtures = ["1_users", "2_initial_data"]

    def setUp(self):
        self.client.login(username="ahankins", password="hahaha")

    def test_post(self):
        op_obj = {
            'workflow_job': "http://localhost:8000/workflowjob/a21f510a16c24701ac0e435b3f4c20f3/",
            'output_port_type': "http://localhost:8000/outputporttype/1cdb067e98194da48dd3dfa35e84671c/",
        }

        response = self.client.post("/outputports/", op_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
