import os
from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework import status

from rodan.models.project import Project

# Refer to http://www.django-rest-framework.org/api-guide/testing


class ProjectViewTestCase(APITestCase):
    fixtures = ["1_users", "2_initial_data"]

    def setUp(self):
        self.media_root = os.path.join(settings.PROJECT_DIR, 'uploads/')

        # self.client is automatically instantiated in APITestCase
        self.client.login(username="ahankins", password="hahaha")
        self.project_dir = os.path.join(self.media_root, "projects/9e8e928b4ec24a09b6113f1b0af1ea53/pages/2f63f986449349769d7a313e0fc6edb3/")

        # we need to fix the file paths on our Page object

    def tearDown(self):
        # tearing this down manually calls the delete method,
        # which cleans up the filesystem
        Project.objects.all().delete()

    # def test_unauthorized(self):
    #     list_projects = self.test_client.get("/projects/")

    def test_get_list(self):
        response = self.client.get("/projects/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_detail(self):
        response = self.client.get("/project/9e8e928b4ec24a09b6113f1b0af1ea53/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post(self):
        proj_obj = {
            "creator": "http://localhost:8000/user/1/",
            "description": "Created Project",
            "name": "Another Test Project",
        }
        response = self.client.post("/projects/", proj_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_put(self):
        pass

    def test_patch(self):
        proj_mod = {"name": "Changing the title"}
        response = self.client.patch("/project/9e8e928b4ec24a09b6113f1b0af1ea53/", proj_mod, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Changing the title")

    def test_delete(self):
        response = self.client.delete("/project/9e8e928b4ec24a09b6113f1b0af1ea53/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(uuid="9e8e928b4ec24a09b6113f1b0af1ea53").exists())
