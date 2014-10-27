from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
from rodan.models import Resource, ResourceType


class ResourceViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
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
                SimpleUploadedFile('page1.txt', 'n/t'),
                SimpleUploadedFile('page2.txt', 'n/t')
            ],
        }
        response = self.client.post("/resources/", resource_obj, format='multipart')
        anticipated_message = {'message': "You must supply project identifier for these resources."}

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(anticipated_message, response.data)

    def test_post(self):
        with self.settings(CELERY_ALWAYS_EAGER=True,
                           CELERY_EAGER_PROPAGATES_EXCEPTIONS=True):  # run celery task synchronously
            resource_obj = {
                'project': "http://localhost:8000/project/{0}/".format(self.test_project.uuid),
                'files': [
                    SimpleUploadedFile('page1.txt', 'n/t'),
                    SimpleUploadedFile('page2.txt', 'n/t')
                ],
                'type': "http://localhost:8000/resourcetype/{0}/".format(ResourceType.cached('application/octet-stream').uuid),
            }
            response = self.client.post("/resources/", resource_obj, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(len(response.data['resources']), 2)
            self.test_resource1 = Resource.objects.get(pk=response.data['resources'][0]['uuid'])
            self.test_resource2 = Resource.objects.get(pk=response.data['resources'][1]['uuid'])
            self.assertNotEqual(self.test_resource1.resource_file.path, '')
            self.assertNotEqual(self.test_resource1.compat_resource_file.path, '')
            self.assertNotEqual(self.test_resource2.resource_file.path, '')
            self.assertNotEqual(self.test_resource2.compat_resource_file.path, '')


    # def test_patch(self):
    #     resource_update = {'resource_type': 'text/plain'}
    #     response = self.client.patch("/resource/8aa7e270b1c54be49dde5a682b16cda7/", resource_update, format='json').data

    #     self.assertEqual(response['resource_type'], 'text/plain')
