from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from rodan.models.resource import Resource
from rodan.models.project import Project


class ResourceViewTestCase(APITestCase):
    fixtures = ['1_users', '2_initial_data']

    def setUp(self):
        self.client.login(username="ahankins", password="hahaha")
        self.test_project = Project.objects.get(name="Test Project")

    def test_post_no_files(self):
        resource_obj = {
            'project': "http://localhost:8000/project/9e8e928b4ec24a09b6113f1b0af1ea53/",
            'resource_order': 1,
        }
        response = self.client.post("/resources/", resource_obj, format='json')
        anticipated_message = {'message': "You must supply at least one file to upload"}

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_post_no_resource_order(self):
        resource_obj = {
            'project': "http://localhost:8000/project/9e8e928b4ec24a09b6113f1b0af1ea53/",
            'files': [
                SimpleUploadedFile('page1.png', 'n/t'),
                SimpleUploadedFile('page2.png', 'n/t')
            ]
        }
        response = self.client.post("/resources/", resource_obj, format='multipart')
        anticipated_message = {'message': "The start sequence for the resource ordering may not be empty."}

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_post_no_project(self):
        resource_obj = {
            'files': [
                SimpleUploadedFile('page1.png', 'n/t'),
                SimpleUploadedFile('page2.png', 'n/t')
            ],
            'resource_order': 1
        }
        response = self.client.post("/resources/", resource_obj, format='multipart')
        anticipated_message = {'message': "You must supply project identifier for these resources."}

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(anticipated_message, response.data)

    def test_post(self):
        resource_obj = {
            'project': "http://localhost:8000/project/9e8e928b4ec24a09b6113f1b0af1ea53/",
            'files': [
                SimpleUploadedFile('page1.png', 'n/t'),
                SimpleUploadedFile('page2.png', 'n/t')
            ],
            'resource_order': 1
        }
        response = self.client.post("/resources/", resource_obj, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['resources']), 2)

    def test_patch(self):
        # write patch method for specifying file type
        pass
