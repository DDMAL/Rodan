from django.test import TestCase
from django.test import Client
from rodan.models.project import Project


class ProjectViewTestCase(TestCase):
    fixtures = ["1_users", "2_inital_data"]

    def setUp(self):
        self.test_client = Client()
        print(Project.objects.all())

    def test_get(self):
        pass

    def test_put(self):
        pass

    def test_patch(self):
        pass

    def test_post(self):
        pass

    def test_delete(self):
        pass
