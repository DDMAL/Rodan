from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from rodan.models.project import Project
from rodan.test.RodanTestHelpers import RodanTestSetUpMixin, RodanTestTearDownMixin


class ResourceViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_basic_workflow()
        self.client.login(username="ahankins", password="hahaha")

    def test_post_no_files(self):
        resource_obj = {
            'project': "http://localhost:8000/project/{0}/".format(self.test_project.uuid),
        }
        response = self.client.post("/resources/", resource_obj, format='json')
        anticipated_message = {'message': "You must supply at least one file to upload"}

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
            'project': "http://localhost:8000/project/{0}/".format(self.test_project.uuid),
            'files': [
                SimpleUploadedFile('page1.png', 'n/t'),
                SimpleUploadedFile('page2.png', 'n/t')
            ],
        }
        response = self.client.post("/resources/", resource_obj, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['resources']), 2)

    # def test_patch(self):
    #     resource_update = {'resource_type': 'text/plain'}
    #     response = self.client.patch("/resource/8aa7e270b1c54be49dde5a682b16cda7/", resource_update, format='json').data

    #     self.assertEqual(response['resource_type'], 'text/plain')
