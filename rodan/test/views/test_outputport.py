from rest_framework.test import APITestCase
from rest_framework import status
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin


class OutputPortViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_basic_workflow()
        self.client.force_authenticate(user=self.test_superuser)

    def test_post(self):
        op_obj = {
            "workflow_job": "http://localhost:8000/api/workflowjob/{0}/".format(
                self.test_workflowjob.uuid
            ),
            "output_port_type": "http://localhost:8000/api/outputporttype/{0}/".format(
                self.test_outputporttype.uuid
            ),
        }

        response = self.client.post("/api/outputports/", op_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
