from rest_framework.test import APITestCase

from rodan.models.resource import Resource
from rodan.models.project import Project


class ResourceViewTestCase(APITestCase):
    fixtures = ['1_users', '2_initial_data']

    def setUp(self):
        pass

    def test_post_no_files(self):
        pass

    def test_post_no_resource_order(self):
        pass

    def test_post_no_project(self):
        pass

    def test_post(self):
        pass

    def test_patch(self):
        # write patch method for specifying file type
        pass
