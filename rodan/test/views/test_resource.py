import os
from StringIO import StringIO

from django.core.files.uploadedfile import SimpleUploadedFile
from model_mommy import mommy
from PIL import Image
from rest_framework.test import APITestCase
from rest_framework import status

from rodan.constants import task_status
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
from rodan.models import Resource, ResourceType


class ResourceViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_basic_workflow()
        self.client.force_authenticate(user=self.test_superuser)

    def test_post_no_files(self):
        resource_obj = {
            "project": "http://localhost:8000/project/{0}/".format(
                self.test_project.uuid
            )
        }
        response = self.client.post("/resources/", resource_obj, format="json")
        anticipated_message = {
            "files": ["You must supply at least one file to upload."]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_post_no_project(self):
        resource_obj = {
            "files": [
                SimpleUploadedFile("page1.txt", "n/t"),
                SimpleUploadedFile("page2.txt", "n/t"),
            ]
        }
        response = self.client.post("/resources/", resource_obj, format="multipart")
        anticipated_message = {"project": ["This field is required."]}

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(anticipated_message, response.data)

    def test_post(self):
        resource_obj = {
            "project": "http://localhost:8000/project/{0}/".format(
                self.test_project.uuid
            ),
            "files": [
                SimpleUploadedFile("page1.txt", "n/t"),
                SimpleUploadedFile("page2.txt", "n/t"),
            ],
            "type": "http://localhost:8000/resourcetype/{0}/".format(
                ResourceType.objects.get(mimetype="application/octet-stream").uuid
            ),
        }
        response = self.client.post("/resources/", resource_obj, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 2)
        self.test_resource1 = Resource.objects.get(pk=response.data[0]["uuid"])
        self.test_resource2 = Resource.objects.get(pk=response.data[1]["uuid"])
        self.assertNotEqual(self.test_resource1.resource_file.path, "")

        # Since writing resourcetype identification, it will correctly identify the test file
        # as a plain text file with mimetype "text/plain". They will not be identified as
        # an "application/octet-stream"
        self.assertEqual(self.test_resource1.resource_type.mimetype, "text/plain")
        self.assertEqual(
            self.test_resource1.processing_status, task_status.NOT_APPLICABLE
        )
        self.assertNotEqual(self.test_resource2.resource_file.path, "")
        self.assertEqual(self.test_resource2.resource_type.mimetype, "text/plain")
        self.assertEqual(
            self.test_resource2.processing_status, task_status.NOT_APPLICABLE
        )

    def test_get_results_of_workflowrun(self):
        wfrun1 = mommy.make("rodan.WorkflowRun")
        wfrun2 = mommy.make("rodan.WorkflowRun")
        r1 = mommy.make("rodan.Resource")
        r2 = mommy.make("rodan.Resource")
        r3 = mommy.make("rodan.Resource")
        output1a = mommy.make("rodan.Output", resource=r1, run_job__workflow_run=wfrun1)
        output1b = mommy.make("rodan.Output", resource=r2, run_job__workflow_run=wfrun1)
        output1c = mommy.make("rodan.Output", resource=r3, run_job__workflow_run=wfrun1)
        res1a = output1a.resource
        res1a.origin = output1a
        res1a.save()
        res1b = output1b.resource
        res1b.origin = output1b
        res1b.save()
        res1c = output1c.resource
        res1c.origin = output1c
        res1c.save()
        mommy.make("rodan.Input", run_job__workflow_run=wfrun1, resource=res1a)

        r4 = mommy.make("rodan.Resource")
        output2 = mommy.make("rodan.Output", resource=r4, run_job__workflow_run=wfrun2)
        res2 = output2.resource
        res2.origin = output2
        res2.save()
        mommy.make("rodan.Input", run_job__workflow_run=wfrun1, resource=res2)

        response = self.client.get(
            "/resources/?format=json&result_of_workflow_run={0}".format(wfrun1.uuid)
        )
        res_list = response.data["results"]
        self.assertEqual(len(res_list), 2)
        self.assertEqual(
            set(map(lambda r: r["uuid"], res_list)),
            set(map(str, [res1b.uuid, res1c.uuid])),
        )

        response = self.client.get(
            "/resources/?format=json&result_of_workflow_run={0}".format(wfrun2.uuid)
        )
        res_list = response.data["results"]
        self.assertEqual(len(res_list), 1)
        self.assertEqual(res_list[0]["uuid"], str(res2.uuid))

    def test_get_with_filter_uploaded(self):
        wfrun1 = mommy.make("rodan.WorkflowRun")
        r1 = mommy.make("rodan.Resource")
        output1a = mommy.make("rodan.Output", resource=r1, run_job__workflow_run=wfrun1)
        res1 = output1a.resource
        res1.origin = output1a
        res1.save()
        mommy.make("rodan.Input", run_job__workflow_run=wfrun1, resource=res1)
        response1 = self.client.get("/resources/?format=json&uploaded=false")
        res_list1 = response1.data["results"]
        self.assertEqual(len(res_list1), 1)
        self.assertEqual(res_list1[0]["uuid"], str(res1.uuid))

        response2 = self.client.get("/resources/?format=json&uploaded=true")
        res_list2 = response2.data["results"]
        self.assertEqual(len(res_list2), 1)
        self.assertEqual(res_list2[0]["uuid"], str(r1.uuid))

    def test_get_resources_in_resourcelist(self):
        rt = mommy.make("rodan.ResourceType")
        r1 = mommy.make("rodan.Resource", project=self.test_project, resource_type=rt)
        r2 = mommy.make("rodan.Resource", project=self.test_project, resource_type=rt)
        r3 = mommy.make("rodan.Resource", project=self.test_project, resource_type=rt)
        r4 = mommy.make("rodan.Resource", project=self.test_project, resource_type=rt)  # noqa
        rl_obj = {
            "resources": map(
                lambda x: "http://localhost:8000/resource/{0}/".format(x.uuid),
                [r1, r2, r3],
            ),
            "project": "http://localhost:8000/project/{0}/".format(
                self.test_project.uuid
            ),
        }
        response = self.client.post("/resourcelists/", rl_obj, format="json")
        assert response.status_code == status.HTTP_201_CREATED, "This should pass"
        rl_uuid = response.data["uuid"]
        rl_url = response.data["url"]

        response1 = self.client.get("/resources/?resource_list={0}".format(rl_uuid))
        res_list1 = response1.data["results"]
        self.assertEqual(len(res_list1), 3)  # search using the uuid of resourcelist

        response2 = self.client.get("/resources/?resource_list={0}".format(rl_url))
        res_list2 = response2.data["results"]
        self.assertEqual(len(res_list2), 3)  # search using the url of resourcelist

        uuid = "11111111-1111-1111-1111-111111111111"
        response3 = self.client.get("/resources/?resource_list={0}".format(uuid))
        res_list3 = response3.data["results"]
        self.assertEqual(len(res_list3), 0)  # not existing resourcelist

        bad_uuid = "11111111-1111-1111-1111-111111111"
        response4 = self.client.get("/resources/?resource_list={0}".format(bad_uuid))
        res_list4 = response4.data["results"]
        self.assertEqual(len(res_list4), 0)  # bad uuid for resourcelist


class ResourceProcessingTestCase(
    RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin
):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_basic_workflow()
        self.client.force_authenticate(user=self.test_user)

    def test_post_image(self):
        # [TODO] When there's time, try these tests again in the Travis Docker image.
        # For whatever reason, this and one another test always fail on travis only.
        # They do not fail locally. Somehow mkstemp silently fails to create a file
        # that subprocess.check_call needs for converting it to a JPEG2000 using
        # kakadu.
        if os.environ["TRAVIS"] != "true":
            file_obj = StringIO()
            image = Image.new("RGB", size=(50, 50), color=(256, 0, 0))
            image.save(file_obj, "png")
            file_obj.name = "page1.png"
            file_obj.seek(0)
            rt = ResourceType.objects.get(mimetype="image/rgb+png")
            resource_obj = {
                "project": "http://localhost:8000/project/{0}/".format(
                    self.test_project.uuid
                ),
                "files": [file_obj],
                "type": "http://localhost:8000/resourcetype/{0}/".format(rt.uuid),
            }
            response = self.client.post(
                "/resources/", resource_obj, format="multipart", resource_type=rt
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.test_resource1 = Resource.objects.get(pk=response.data[0]["uuid"])
            self.assertNotEqual(self.test_resource1.resource_file.path, "")
            self.assertEqual(self.test_resource1.resource_type.mimetype, "image/rgb+png")

    def test_post_image_claiming_txt(self):
        file_obj = StringIO()
        image = Image.new("RGBA", size=(50, 50), color=(256, 0, 0))
        image.save(file_obj, "png")
        file_obj.name = "page1.png"
        file_obj.seek(0)
        resource_obj = {
            "project": "http://localhost:8000/project/{0}/".format(
                self.test_project.uuid
            ),
            "files": [file_obj],
            "type": "text/plain",
        }
        response = self.client.post("/resources/", resource_obj, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.test_resource1 = Resource.objects.get(pk=response.data[0]["uuid"])
        self.assertNotEqual(self.test_resource1.resource_file.path, "")
        self.assertEqual(
            self.test_resource1.processing_status, task_status.NOT_APPLICABLE
        )
        self.assertEqual(self.test_resource1.resource_type.mimetype, "text/plain")

    def test_post_bad_image(self):
        with self.settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=False):
            resource_obj = {
                "project": "http://localhost:8000/project/{0}/".format(
                    self.test_project.uuid
                ),
                "files": [SimpleUploadedFile("test_page1.png", "n/t")],
            }
            try:
                response = self.client.post(
                    "/resources/", resource_obj, format="multipart"
                )
            except IOError:
                pass
            else:
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.test_resource1 = Resource.objects.get(name="test_page1")
            # self.assertEqual(
            #   self.test_resource1.resource_type.mimetype,
            #   "application/octet-stream"
            # )
            self.assertEqual(self.test_resource1.resource_type.mimetype, "text/plain")

    # Incomplete test. Might try to step away from all patch requests and do something else anyway.
    # def test_patch(self):
    #     resource_update = {'resource_type': 'text/plain'}
    #     response = self.client.patch(
    #       "/resource/8aa7e270b1c54be49dde5a682b16cda7/",
    #       resource_update, format='json').data
    #     self.assertEqual(response['resource_type'], 'text/plain')
