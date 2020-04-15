from rest_framework.test import APITestCase
from rest_framework import status
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
from rodan.models.project import Project

# Refer to http://www.django-rest-framework.org/api-guide/testing


class ProjectViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_basic_workflow()
        self.client.force_authenticate(user=self.test_superuser)

    def test_get_list(self):
        response = self.client.get("/api/projects/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_detail(self):
        response = self.client.get("/api/project/{0}/".format(self.test_project.uuid))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post(self):
        proj_obj = {
            "creator": "http://localhost:8000/api/user/{0}/".format(self.test_user.pk),
            "description": "Created Project",
            "name": "Another Test Project",
        }
        response = self.client.post("/api/projects/", proj_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_patch(self):
        proj_mod = {"name": "Changing the title"}
        response = self.client.patch(
            "/api/project/{0}/".format(self.test_project.uuid), proj_mod, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Changing the title")

    def test_delete(self):
        project_uuid = self.test_project.uuid
        response = self.client.delete("/api/project/{0}/?format=json".format(project_uuid))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(uuid=project_uuid).exists())
