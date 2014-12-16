from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rodan.models import ResourceAssignment
from model_mommy import mommy
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
import uuid

class ResourceAssignmentViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.client.login(username="ahankins", password="hahaha")
        self.test_inputport = mommy.make('rodan.InputPort')
        self.test_workflow = self.test_inputport.workflow_job.workflow
        self.test_project = self.test_workflow.project

    def test_get_list(self):
        ra = mommy.make('rodan.ResourceAssignment', workflow=self.test_workflow)
        response = self.client.get("/resourceassignments/")
        self.assertEqual(ra.uuid.hex, response.data['results'][0]['uuid'])
    def test_get_detail(self):
        ra = mommy.make('rodan.ResourceAssignment', workflow=self.test_workflow)
        response = self.client.get("/resourceassignment/{0}/".format(ra.uuid.hex))
        self.assertEqual(ra.uuid.hex, response.data['uuid'])

    def test_post_resource(self):
        res = mommy.make('rodan.Resource',
                         project=self.test_project)
        ra_obj = {
            'input_port': "http://localhost:8000/inputport/{0}/".format(self.test_inputport.uuid.hex),
            'resource': 'http://localhost:8000/resource/{0}/'.format(res.uuid.hex)
        }
        response = self.client.post("/resourceassignments/", ra_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    def test_post_resourcecollection(self):
        rc = mommy.make('rodan.ResourceCollection',
                        workflow=self.test_workflow)
        ra_obj = {
            'input_port': "http://localhost:8000/inputport/{0}/".format(self.test_inputport.uuid.hex),
            'resource_collection': 'http://localhost:8000/resourcecollection/{0}/'.format(rc.uuid.hex)
        }
        response = self.client.post("/resourceassignments/", ra_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_neither(self):
        ra_obj = {
            'input_port': "http://localhost:8000/inputport/{0}/".format(self.test_inputport.uuid.hex),
        }
        anticipated_message = {'non_field_errors': ["The ResourceAssignment should have either one Resource or one ResourceCollection."]}
        response = self.client.post("/resourceassignments/", ra_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)
    def test_post_both(self):
        res = mommy.make('rodan.Resource',
                         project=self.test_project)
        rc = mommy.make('rodan.ResourceCollection',
                        workflow=self.test_workflow)
        ra_obj = {
            'input_port': "http://localhost:8000/inputport/{0}/".format(self.test_inputport.uuid.hex),
            'resource_collection': 'http://localhost:8000/resourcecollection/{0}/'.format(rc.uuid.hex),
            'resource': 'http://localhost:8000/resource/{0}/'.format(res.uuid.hex)
        }
        anticipated_message = {'non_field_errors': ["The ResourceAssignment should not have both Resource and ResourceCollection."]}
        response = self.client.post("/resourceassignments/", ra_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_post_conflict_resource(self):
        res = mommy.make('rodan.Resource')
        ra_obj = {
            'input_port': "http://localhost:8000/inputport/{0}/".format(self.test_inputport.uuid.hex),
            'resource': 'http://localhost:8000/resource/{0}/'.format(res.uuid.hex)
        }
        anticipated_message = {'non_field_errors': ["The InputPort is not in the same project as Resource."]}
        response = self.client.post("/resourceassignments/", ra_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)
    def test_post_conflict_resourcecollection(self):
        rc = mommy.make('rodan.ResourceCollection')
        ra_obj = {
            'input_port': "http://localhost:8000/inputport/{0}/".format(self.test_inputport.uuid.hex),
            'resource_collection': 'http://localhost:8000/resourcecollection/{0}/'.format(rc.uuid.hex)
        }
        anticipated_message = {'non_field_errors': ["The InputPort is not in the same workflow as ResourceCollection."]}
        response = self.client.post("/resourceassignments/", ra_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_patch_modify_resource(self):
        ra = mommy.make('rodan.ResourceAssignment',
                        input_port=self.test_inputport,
                        resource__project=self.test_project)
        new_res = mommy.make('rodan.Resource', project=self.test_project)
        obj = {
            'resource': "http://localhost:8000/resource/{0}/".format(new_res.uuid.hex)
        }
        response = self.client.patch("/resourceassignment/{0}/".format(ra.uuid.hex), obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_patch_modify_resource_conflict(self):
        ra = mommy.make('rodan.ResourceAssignment',
                        input_port=self.test_inputport,
                        resource__project=self.test_project)
        conflict_res = mommy.make('rodan.Resource')
        obj = {
            'resource': "http://localhost:8000/resource/{0}/".format(conflict_res.uuid.hex)
        }
        anticipated_message = {'non_field_errors': ["The InputPort is not in the same project as Resource."]}
        response = self.client.patch("/resourceassignment/{0}/".format(ra.uuid.hex), obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)
    def test_patch_remove_resource(self):
        ra = mommy.make('rodan.ResourceAssignment',
                        input_port=self.test_inputport,
                        resource__project=self.test_project)
        obj = {
            'resource': None
        }
        anticipated_message = {'non_field_errors': ["The ResourceAssignment should have either one Resource or one ResourceCollection."]}
        response = self.client.patch("/resourceassignment/{0}/".format(ra.uuid.hex), obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)
    def test_patch_add_resourcecollection(self):
        ra = mommy.make('rodan.ResourceAssignment',
                        input_port=self.test_inputport,
                        resource__project=self.test_project)
        new_rc = mommy.make('rodan.ResourceCollection',
                            workflow=self.test_workflow)
        obj = {
            'resource_collection': "http://localhost:8000/resourcecollection/{0}/".format(new_rc.uuid.hex)
        }
        anticipated_message = {'non_field_errors': ["The ResourceAssignment should not have both Resource and ResourceCollection."]}
        response = self.client.patch("/resourceassignment/{0}/".format(ra.uuid.hex), obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)
    def test_patch_replace_with_resourcecollection(self):
        ra = mommy.make('rodan.ResourceAssignment',
                        input_port=self.test_inputport,
                        resource__project=self.test_project)
        new_rc = mommy.make('rodan.ResourceCollection',
                            workflow=self.test_workflow)
        obj = {
            'resource': None,
            'resource_collection': "http://localhost:8000/resourcecollection/{0}/".format(new_rc.uuid.hex)
        }
        response = self.client.patch("/resourceassignment/{0}/".format(ra.uuid.hex), obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_modify_resourcecollection(self):
        ra = mommy.make('rodan.ResourceAssignment',
                        input_port=self.test_inputport,
                        resource_collection__workflow=self.test_workflow)
        new_rc = mommy.make('rodan.ResourceCollection', workflow=self.test_workflow)
        obj = {
            'resource_collection': "http://localhost:8000/resourcecollection/{0}/".format(new_rc.uuid.hex)
        }
        response = self.client.patch("/resourceassignment/{0}/".format(ra.uuid.hex), obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_patch_modify_resourcecollection_conflict(self):
        ra = mommy.make('rodan.ResourceAssignment',
                        input_port=self.test_inputport,
                        resource_collection__workflow=self.test_workflow)
        new_rc = mommy.make('rodan.ResourceCollection')
        obj = {
            'resource_collection': "http://localhost:8000/resourcecollection/{0}/".format(new_rc.uuid.hex)
        }
        anticipated_message = {'non_field_errors': ["The InputPort is not in the same workflow as ResourceCollection."]}
        response = self.client.patch("/resourceassignment/{0}/".format(ra.uuid.hex), obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)
    def test_patch_remove_resourcecollection(self):
        ra = mommy.make('rodan.ResourceAssignment',
                        input_port=self.test_inputport,
                        resource_collection__workflow=self.test_workflow)
        obj = {
            'resource_collection': None
        }
        anticipated_message = {'non_field_errors': ["The ResourceAssignment should have either one Resource or one ResourceCollection."]}
        response = self.client.patch("/resourceassignment/{0}/".format(ra.uuid.hex), obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_delete(self):
        ra = mommy.make('rodan.ResourceAssignment')
        ra_uuid = ra.uuid.hex
        response = self.client.delete("/resourceassignment/{0}/.json".format(ra_uuid), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ResourceAssignment.objects.filter(pk=ra_uuid).exists())
