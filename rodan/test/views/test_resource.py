from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
from rodan.models import Resource, ResourceType
from rodan.models.resource import ResourceProcessingStatus
from StringIO import StringIO
from PIL import Image
from model_mommy import mommy


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
        anticipated_message = {'files': ["You must supply at least one file to upload."]}

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
        anticipated_message = {'project': ['This field is required.']}

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(anticipated_message, response.data)

    def test_post(self):
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
        self.assertEqual(len(response.data), 2)
        self.test_resource1 = Resource.objects.get(pk=response.data[0]['uuid'])
        self.test_resource2 = Resource.objects.get(pk=response.data[1]['uuid'])
        self.assertNotEqual(self.test_resource1.resource_file.path, '')
        self.assertNotEqual(self.test_resource1.compat_resource_file.path, '')
        self.assertEqual(self.test_resource1.resource_type.mimetype, 'application/octet-stream')
        self.assertEqual(self.test_resource1.processing_status, ResourceProcessingStatus.NOT_APPLICABLE)
        self.assertNotEqual(self.test_resource2.resource_file.path, '')
        self.assertNotEqual(self.test_resource2.compat_resource_file.path, '')
        self.assertEqual(self.test_resource2.resource_type.mimetype, 'application/octet-stream')
        self.assertEqual(self.test_resource2.processing_status, ResourceProcessingStatus.NOT_APPLICABLE)

    def test_get_results_of_workflowrun(self):
        wfrun1 = mommy.make('rodan.WorkflowRun')
        wfrun2 = mommy.make('rodan.WorkflowRun')
        output1a = mommy.make('rodan.Output',
                              run_job__workflow_run=wfrun1)
        output1b = mommy.make('rodan.Output',
                              run_job__workflow_run=wfrun1)
        output1c = mommy.make('rodan.Output',
                              run_job__workflow_run=wfrun1)
        res1a = output1a.resource
        res1a.origin = output1a
        res1a.save()
        res1b = output1b.resource
        res1b.origin = output1b
        res1b.save()
        res1c = output1c.resource
        res1c.origin = output1c
        res1c.save()
        mommy.make('rodan.Input',
                   run_job__workflow_run=wfrun1,
                   resource=res1a)

        output2 = mommy.make('rodan.Output',
                             run_job__workflow_run=wfrun2)
        res2 = output2.resource
        res2.origin = output2
        res2.save()
        mommy.make('rodan.Input',
                   run_job__workflow_run=wfrun1,
                   resource=res2)

        response = self.client.get("/resources/?format=json&result_of_workflow_run={0}".format(wfrun1.uuid))
        res_list = response.data['results']
        self.assertEqual(len(res_list), 2)
        self.assertEqual(set(map(lambda r: r['uuid'], res_list)), set(map(str, [res1b.uuid, res1c.uuid])))

        response = self.client.get("/resources/?format=json&result_of_workflow_run={0}".format(wfrun2.uuid))
        res_list = response.data['results']
        self.assertEqual(len(res_list), 1)
        self.assertEqual(res_list[0]['uuid'], str(res2.uuid))


class ResourceProcessingTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_basic_workflow()
        self.client.login(username="ahankins", password="hahaha")

    def test_post_image(self):
        file_obj = StringIO()
        image = Image.new("RGBA", size=(50, 50), color=(256, 0, 0))
        image.save(file_obj, 'png')
        file_obj.name = 'page1.png'
        file_obj.seek(0)
        resource_obj = {
            'project': "http://localhost:8000/project/{0}/".format(self.test_project.uuid),
            'files': [
                file_obj
            ],
        }
        response = self.client.post("/resources/", resource_obj, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.test_resource1 = Resource.objects.get(pk=response.data[0]['uuid'])
        self.assertNotEqual(self.test_resource1.compat_resource_file.path, '')
        self.assertEqual(self.test_resource1.processing_status, ResourceProcessingStatus.HAS_FINISHED)
        self.assertEqual(self.test_resource1.resource_type.mimetype, 'image/rgb+png')

    def test_post_image_claiming_txt(self):
        file_obj = StringIO()
        image = Image.new("RGBA", size=(50, 50), color=(256, 0, 0))
        image.save(file_obj, 'png')
        file_obj.name = 'page1.png'
        file_obj.seek(0)
        resource_obj = {
            'project': "http://localhost:8000/project/{0}/".format(self.test_project.uuid),
            'files': [
                file_obj
            ],
            'type': 'text/plain'
        }
        response = self.client.post("/resources/", resource_obj, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.test_resource1 = Resource.objects.get(pk=response.data[0]['uuid'])
        self.assertNotEqual(self.test_resource1.compat_resource_file.path, '')
        self.assertEqual(self.test_resource1.processing_status, ResourceProcessingStatus.NOT_APPLICABLE)
        self.assertEqual(self.test_resource1.resource_type.mimetype, 'application/octet-stream')

    def test_post_bad_image(self):
        with self.settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=False):
            resource_obj = {
                'project': "http://localhost:8000/project/{0}/".format(self.test_project.uuid),
                'files': [
                    SimpleUploadedFile('test_page1.png', 'n/t'),
                ],
            }
            try:
                # Cannot figure out why Celery still raises exception with propagation turning off.
                response = self.client.post("/resources/", resource_obj, format='multipart')
            except IOError:
                pass
            else:
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.test_resource1 = Resource.objects.get(name="test_page1.png")
            self.assertFalse(self.test_resource1.compat_resource_file)
            self.assertEqual(self.test_resource1.processing_status, ResourceProcessingStatus.FAILED)
            self.assertEqual(self.test_resource1.resource_type.mimetype, 'application/octet-stream')




    # def test_patch(self):
    #     resource_update = {'resource_type': 'text/plain'}
    #     response = self.client.patch("/resource/8aa7e270b1c54be49dde5a682b16cda7/", resource_update, format='json').data

    #     self.assertEqual(response['resource_type'], 'text/plain')
