from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rodan.models import ResourceCollection
from model_mommy import mommy
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
import uuid

class ResourceCollectionViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.client.login(username="ahankins", password="hahaha")
        self.test_workflow = mommy.make('rodan.Workflow')
        self.test_project = self.test_workflow.project

    def test_get_list(self):
        rc = mommy.make('rodan.ResourceCollection', workflow=self.test_workflow)
        response = self.client.get("/resourcecollections/")
        self.assertEqual(rc.uuid.hex, response.data['results'][0]['uuid'])

    def test_post_empty(self):
        rc_obj = {
            'workflow': "http://localhost:8000/workflow/{0}/".format(self.test_workflow.uuid)
        }
        response = self.client.post("/resourcecollections/", rc_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_with_resources(self):
        rs = mommy.make('rodan.Resource', project=self.test_project, _quantity=10)
        rc_obj = {
            'workflow': "http://localhost:8000/workflow/{0}/".format(self.test_workflow.uuid),
            'resources': map(lambda r: "http://localhost:8000/resource/{0}/".format(r.uuid), rs)
        }
        response = self.client.post("/resourcecollections/", rc_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_with_conflict_resources(self):
        r_1 = mommy.make('rodan.Resource', project=self.test_project)
        r_2 = mommy.make('rodan.Resource')
        rs = (r_1, r_2)
        rc_obj = {
            'workflow': "http://localhost:8000/workflow/{0}/".format(self.test_workflow.uuid),
            'resources': map(lambda r: "http://localhost:8000/resource/{0}/".format(r.uuid), rs)
        }
        response = self.client.post("/resourcecollections/", rc_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'non_field_errors': ['Resource {0} is not in the same project as the Workflow'.format(r_2.uuid.hex)]})

    def test_patch_resources(self):
        rc = mommy.make('rodan.ResourceCollection', workflow=self.test_workflow)
        rc_uuid = rc.uuid.hex
        rs = mommy.make('rodan.Resource', project=self.test_project, _quantity=10)
        rc_obj = {
            'resources': map(lambda r: "http://localhost:8000/resource/{0}/".format(r.uuid), rs)
        }
        response = self.client.patch("/resourcecollection/{0}/".format(rc_uuid), rc_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(rc.resources.all()), 10)

    def test_patch_conflict_resources(self):
        rc = mommy.make('rodan.ResourceCollection', workflow=self.test_workflow)
        rc_uuid = rc.uuid.hex
        r_1 = mommy.make('rodan.Resource', project=self.test_project)
        r_2 = mommy.make('rodan.Resource')
        rs = (r_1, r_2)
        rc_obj = {
            'resources': map(lambda r: "http://localhost:8000/resource/{0}/".format(r.uuid), rs)
        }
        response = self.client.patch("/resourcecollection/{0}/".format(rc_uuid), rc_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'non_field_errors': ['Resource {0} is not in the same project as the Workflow'.format(r_2.uuid.hex)]})
        self.assertEqual(len(rc.resources.all()), 0)

    def test_delete(self):
        rc = mommy.make('rodan.ResourceCollection')
        rc_uuid = rc.uuid.hex
        response = self.client.delete("/resourcecollection/{0}/.json".format(rc_uuid), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ResourceCollection.objects.filter(pk=rc_uuid).exists())
