from rest_framework.test import APITestCase
from rest_framework import status
from rodan.models import ResourceList
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
from model_mommy import mommy


class ResourceListViewTestCase(
    RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin
):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.test_project = mommy.make("rodan.Project")
        self.test_resourcetype = mommy.make("rodan.ResourceType")
        self.test_resources = mommy.make(
            "rodan.Resource",
            _quantity=5,
            project=self.test_project,
            resource_type=self.test_resourcetype,
        )
        self.client.force_authenticate(user=self.test_superuser)

    def test_create_successfully(self):
        rl_obj = {
            "resources": map(
                # lambda x: "http://localhost:8000/api/resource/{0}/".format(x.uuid),
                lambda x: reverse("resource-detail", kwargs={"pk": x.uuid}),
                self.test_resources,
            ),
            "name": "test resource list",
            # "project": "http://localhost:8000/api/project/{0}/".format(
            "project": reverse("project-detail", kwargs={"pk": self.test_project.uuid}),
        }
        # response = self.client.post("/api/resourcelists/", rl_obj, format="json")
        response = self.client.post(reverse("resourcelist-list"), rl_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        rl_uuid = response.data["uuid"]
        rl = ResourceList.objects.get(uuid=rl_uuid)
        self.assertEqual(rl.project, self.test_project)
        self.assertEqual(rl.resource_type, self.test_resourcetype)
        self.assertEqual(rl.resources.count(), 5)
        resources = rl.resources.all()
        self.assertEqual(resources[0], self.test_resources[0])
        self.assertEqual(resources[1], self.test_resources[1])
        self.assertEqual(resources[2], self.test_resources[2])
        self.assertEqual(resources[3], self.test_resources[3])
        self.assertEqual(resources[4], self.test_resources[4])

    def test_create_conflict_project(self):
        p2 = mommy.make("rodan.Project")
        r2 = mommy.make(
            "rodan.Resource", project=p2, resource_type=self.test_resourcetype
        )
        rl_obj = {
            "resources": map(
                # lambda x: "http://localhost:8000/api/resource/{0}/".format(x.uuid),
                lambda x: reverse("resource-detail", kwargs={"pk": x.uuid}),
                self.test_resources + [r2],
            ),
            "name": "test resource list",
            # "project": "http://localhost:8000/api/project/{0}/".format(p2.uuid),
            "project": reverse("project-detail", kwargs={"pk": p2.uuid}),
        }
        # response = self.client.post("/api/resourcelists/", rl_obj, format="json")
        response = self.client.post(reverse("resourcelist-list"), rl_obj, format="json")
        anticipated_message = {
            "resources": ["All Resources should belong to the same Project."]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_create_conflict_resourcetype(self):
        p2 = mommy.make("rodan.Project")
        rt2 = mommy.make("rodan.ResourceType")
        r2 = mommy.make("rodan.Resource", project=self.test_project, resource_type=rt2)
        rl_obj = {
            "resources": map(
                # lambda x: "http://localhost:8000/api/resource/{0}/".format(x.uuid),
                lambda x: reverse("resource-detail", kwargs={"pk": x.uuid}),
                self.test_resources + [r2],
            ),
            "name": "test resource list",
            # "project": "http://localhost:8000/api/project/{0}/".format(p2.uuid),
            "project": reverse("project-detail", kwargs={"pk": p2.uuid}),
        }
        response = self.client.post(reverse("resourcelist-list"), rl_obj, format="json")
        anticipated_message = {
            "resources": ["All Resources should have the same ResourceType."]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_patch_conflict_resourcetype(self):
        rl_obj = {
            "resources": map(
                # lambda x: "http://localhost:8000/api/resource/{0}/".format(x.uuid),
                lambda x: reverse("resource-detail", kwargs={"pk": x.uuid}),
                self.test_resources,
            ),
            "name": "test resource list",
            # "project": "http://localhost:8000/api/project/{0}/".format(
            #     self.test_project.uuid
            # ),
            "project": reverse("project-detail", kwargs={"pk": self.test_project.uuid}),
        }
        response = self.client.post(reverse("resourcelist-list"), rl_obj, format="json")
        assert response.status_code == status.HTTP_201_CREATED, "This should pass"
        rl_uuid = response.data["uuid"]

        rt2 = mommy.make("rodan.ResourceType")
        r2 = mommy.make("rodan.Resource", project=self.test_project, resource_type=rt2)
        rl_obj = {
            "resources": map(
                # lambda x: "http://localhost:8000/api/resource/{0}/".format(x.uuid),
                lambda x: reverse("resource-detail", kwargs={"pk": x.uuid}),
                self.test_resources + [r2],
            ),
            # "project": "http://localhost:8000/api/project/{0}/".format(
            #     self.test_project.uuid
            # ),
            "project": reverse("project-detail", kwags={"pk": self.test_project.uuid}),
        }
        response = self.client.patch(
            # "/api/resourcelist/{0}/".format(rl_uuid), rl_obj, format="json"
            reverse("resourcelist-detail", kwargs={"pk": rl_uuid}), rl_obj, format="json"
        )
        anticipated_message = {
            "resources": ["All Resources should have the same ResourceType."]
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_patch_conflict_project(self):
        rl_obj = {
            "resources": map(
                # lambda x: "http://localhost:8000/api/resource/{0}/".format(x.uuid),
                lambda x: reverse("resource-detail", kwargs={"pk": x.uuid}),
                self.test_resources,
            ),
            "name": "test resource list",
            # "project": "http://localhost:8000/api/project/{0}/".format(
            #     self.test_project.uuid
            # ),
            "project": reverse("project-detail", kwargs={"pk", self.test_project.uuid})
        }
        # response = self.client.post("/api/resourcelists/", rl_obj, format="json")
        response = self.client.post(
            reverse("resourcelist-list"), rl_obj, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED, "This should pass"
        rl_uuid = response.data["uuid"]

        p2 = mommy.make("rodan.Project")
        r2 = mommy.make(
            "rodan.Resource", project=p2, resource_type=self.test_resourcetype
        )
        rl_obj = {
            "resources": map(
                # lambda x: "http://localhost:8000/api/resource/{0}/".format(x.uuid),
                lambda x: reverse("resource-detail", kwags={"pk": x.uuid}),
                self.test_resources + [r2],
            ),
            # "project": "http://localhost:8000/api/project/{0}/".format(p2.uuid),
            "project": reverse("project-detail", kwargs={"pk": p2.uuid}),
        }
        response = self.client.patch(
            # "/api/resourcelist/{0}/".format(rl_uuid), rl_obj, format="json"
            reverse("resourcelist-detail", kwargs={"pk": rl_uuid}), rl_obj, format="json"
        )
        anticipated_message = {
            "resources": ["All Resources should belong to the same Project."]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_create_empty_resourcelist(self):
        p2 = mommy.make("rodan.Project")
        rl_obj1 = {
            "resources": [],
            "name": "test resource list1",
            # "project": "http://localhost:8000/api/project/{0}/".format(p2.uuid),
            "project": reverse("project-detail", kwargs={"pk": p2.uuid}),
        }
        # response = self.client.post("/api/resourcelists/", rl_obj1, format="json")
        response = self.client.post(reverse("resourcelist-list"), rl_obj1, format="json")
        assert response.status_code == status.HTTP_201_CREATED, "This should pass"
        rl1 = ResourceList.objects.get(name=u'test resource list1')
        self.assertEqual(rl1.get_resource_type().mimetype, "application/octet-stream")

        rl_obj2 = {
            "name": "test resource list2",
            # "project": "http://localhost:8000/api/project/{0}/".format(p2.uuid),
            "project": reverse("project-detail", kwargs={"pk": p2.uuid}),
        }
        # response = self.client.post("/api/resourcelists/", rl_obj2, format="json")
        response = self.client.post(reverse("resourcelist-list"), rl_obj2, format="json")
        assert response.status_code == status.HTTP_201_CREATED, "This should pass"
        rl2 = ResourceList.objects.get(name="test resource list2")
        self.assertEqual(rl2.get_resource_type().mimetype, "application/octet-stream")

        rl_obj3 = {"resources": [], "name": "test resource list3"}
        # response = self.client.post("/api/resourcelists/", rl_obj3, format="json")
        response = self.client.post(reverse("resourcelist-list"), rl_obj3, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_empty_resourcelist(self):
        rl_obj = {
            "resources": map(
                # lambda x: "http://localhost:8000/api/resource/{0}/".format(x.uuid),
                lambda x: reverse("resource-detail", kwargs={"pk": x.uuid}),
                self.test_resources,
            ),
            "name": "test resource list",
            # "project": "http://localhost:8000/api/project/{0}/".format(
            "project": reverse("project-detail", kwargs={"pk": self.test_project.uuid}),
        }
        response = self.client.post("/api/resourcelists/", rl_obj, format="json")
        assert response.status_code == status.HTTP_201_CREATED, "This should pass"
        rl_uuid = response.data["uuid"]

        rl_obj = {
            "resources": [],
            # "project": "http://localhost:8000/api/project/{0}/".format(
            #     self.test_project.uuid
            # ),
            "project": reverse("project-detail", kwargs={"pk": self.test_project.uuid}),
        }
        response = self.client.patch(
            # "/api/resourcelist/{0}/".format(rl_uuid), rl_obj, format="json"
            reverse("resourcelist-detail", kwargs={"pk": rl_uuid}), rl_obj, format="json"
        )
        assert response.status_code == status.HTTP_200_OK, "This should pass"
