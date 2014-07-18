from rest_framework.test import APITestCase
from rest_framework import status


class InputPortTypeViewTestCase(APITestCase):
    fixtures = ["1_users", "2_initial_data"]

    def setUp(self):
        self.client.login(username="ahankins", password="hahaha")

    def test_post(self):
        ipt_obj = {
            'job': "http://localhost:8000/job/0dc1f345b6ad4a8c8739e092e6ff7c2d/",
            'resource_type': 0,
            'minimum': 1,
            'maximum': 1
        }

        response = self.client.post("/inputporttypes/", ipt_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
