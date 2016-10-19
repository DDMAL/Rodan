import os, json
from rest_framework.test import APITestCase
from rest_framework import status

from rodan.models import WorkflowRun, ResourceType
from model_mommy import mommy
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
import uuid
from django.core.files.base import ContentFile
from rodan.constants import task_status

class WorkflowRunViewTest(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_simple_dummy_workflow()
        self.client.force_authenticate(user=self.test_superuser)
        response = self.client.patch("/workflow/{0}/".format(self.test_workflow.uuid), {'valid': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list(self):
        response = self.client.get("/workflowruns/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_no_workflow_ID(self):
        workflowrun_obj = {}

        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {'workflow': ['This field is required.']}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_no_existing_workflow(self):
        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(uuid.uuid1()),
        }

        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {'workflow': ['Invalid hyperlink - Object does not exist.']}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_status(self):
#        anticipated_message = {'status': ['Can only create a WorkflowRun that has SCHEDULED status.']}
	anticipated_message = {'status': ['Can only create a WorkflowRun that requests processing.']}
        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'status': task_status.CANCELLED,
        }

        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        workflowrun_obj['status'] = task_status.FINISHED
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        workflowrun_obj['status'] = task_status.FAILED
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        workflowrun_obj['status'] = task_status.PROCESSING
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        workflowrun_obj['status'] = task_status.REQUEST_CANCELLING
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        workflowrun_obj['status'] = task_status.REQUEST_RETRYING
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_invalid_workflow(self):
        self.test_workflow.valid = False
        self.test_workflow.save()
        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'status': task_status.REQUEST_PROCESSING
#            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid)
        }

        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {'workflow': ["Workflow must be valid before you can run it."]}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_patch_not_found(self):
        workflowrun_update = {'status': task_status.CANCELLED}
        response = self.client.patch("/workflowrun/{0}/".format(uuid.uuid1()), workflowrun_update, format='json')
        anticipated_message = {'detail': 'Not found.'}
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(anticipated_message, response.data)


class WorkflowRunResourceAssignmentTest(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_complex_dummy_workflow()
        self.client.force_authenticate(user=self.test_superuser)
        response = self.client.patch("/workflow/{0}/".format(self.test_workflow.uuid), {'valid': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_valid_assignment(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'resource_assignments': ra
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_valid_assignment__with_list_of_resource_lists(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        ra[self.url(self.test_Dip1)] = [self.url(self.test_resource)]
        ra[self.url(self.test_Fip1)] = [self.url(self.test_resource)]

        resource_lists = []
        for i in range(10):
            rl = mommy.make('rodan.ResourceList',
                            project=self.test_project,
                            resource_type=ResourceType.objects.get(mimetype='test/a2')
            )
            rs = mommy.make(
                'rodan.Resource', _quantity=5,
                project=self.test_project,
                resource_type = ResourceType.objects.get(mimetype='test/a2')
            )
            for index, res in enumerate(rs):
                res.name = str(index) # 0 to 9
                res.save()
                res.resource_file.save('dummy.txt', ContentFile('dummy text'))
            rl.resources.add(*rs)
            resource_lists.append(rl)
        ra[self.url(self.test_Dip3)] = map(self.url, resource_lists)

        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'resource_assignments': ra
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_no_resource_assignments(self):
        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {'resource_assignments': ['This field is required']}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_json_object(self):
        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'resource_assignments': []  # not a JSON object
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {'resource_assignments': ['This field must be a JSON object']}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_satisfied_input_port(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        ra[self.url(self.test_Eip1)] = [self.url(self.test_resource)]
        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'resource_assignments': ra
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {'resource_assignments': {self.url(self.test_Eip1): ['Assigned InputPort must be unsatisfied']}}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_invalid_input_port(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        ra["invalid url"] = [self.url(self.test_resource)]
        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'resource_assignments': ra
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {'resource_assignments': {'invalid url': [u'Invalid hyperlink - No URL match.']}}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_still_unsatisfied_input_port(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        del ra[self.url(self.test_Aip)]
        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'resource_assignments': ra
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {'resource_assignments': ['There are still unsatisfied InputPorts: {0}'.format(self.url(self.test_Aip))]}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resources_not_a_list(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        ra[self.url(self.test_Aip)] = self.url(self.test_resource)
        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'resource_assignments': ra
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {'resource_assignments': {self.url(self.test_Aip): ['A list of resources or resource lists is expected']}}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_resources_empty(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        ra[self.url(self.test_Aip)] = []
        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'resource_assignments': ra
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {'resource_assignments': {self.url(self.test_Aip): ['It is not allowed to assign an empty resource set']}}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_multiple_resource_sets(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        ra[self.url(self.test_Fip1)].pop()
        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'resource_assignments': ra
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message1 = {'resource_assignments': {self.url(self.test_Fip1): ['It is not allowed to assign multiple resource sets']}}
        anticipated_message2 = {'resource_assignments': {self.url(self.test_Dip1): ['It is not allowed to assign multiple resource sets']}}
        self.assertIn(response.data, [anticipated_message1, anticipated_message2])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_resource_not_in_project(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        res = self.test_resourcecollection[5]
        res.project = mommy.make('rodan.Project')
        res.save()
        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'resource_assignments': ra
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message1 = {'resource_assignments': {self.url(self.test_Fip1): {5: ['Resource or ResourceList is not in the project of Workflow']}}}
        anticipated_message2 = {'resource_assignments': {self.url(self.test_Dip1): {5: ['Resource or ResourceList is not in the project of Workflow']}}}
        self.assertIn(response.data, [anticipated_message1, anticipated_message2])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_resource_type_not_match(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        res = self.test_resourcecollection[5]
        res.resource_type = ResourceType.objects.get(mimetype='test/b')
        res.save()
        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'resource_assignments': ra
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message1 = {'resource_assignments': {self.url(self.test_Fip1): {5: ['The resource type does not match the InputPort']}}}
        anticipated_message2 = {'resource_assignments': {self.url(self.test_Dip1): {5: ['The resource type does not match the InputPort']}}}
        self.assertIn(response.data, [anticipated_message1, anticipated_message2])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_resource_to_list_ports(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        pos = len(self.test_resourcecollection)
        ra[self.url(self.test_Dip1)].append(self.url(self.test_resourcelist))
        ra[self.url(self.test_Fip1)].append(self.url(self.test_resourcelist))
        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'resource_assignments': ra
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message1 = {'resource_assignments': {self.url(self.test_Fip1): {pos: ['The InputPort requires Resources but is provided with ResourceLists']}}}
        anticipated_message2 = {'resource_assignments': {self.url(self.test_Dip1): {pos: ['The InputPort requires Resources but is provided with ResourceLists']}}}
        self.assertIn(response.data, [anticipated_message1, anticipated_message2])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_assign_resource_list_to_nonlist_ports(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        ra[self.url(self.test_Dip3)] = map(self.url, self.test_resourcecollection)
        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'resource_assignments': ra
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {'resource_assignments': {self.url(self.test_Dip3): {0: ['The InputPort requires ResourceLists but is provided with Resources']}}}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resource_list_not_in_project(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        self.test_resourcelist.project = mommy.make('rodan.Project')
        self.test_resourcelist.save()
        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'resource_assignments': ra
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {'resource_assignments': {self.url(self.test_Dip3): {0: ['Resource or ResourceList is not in the project of Workflow']}}}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_resource_type_not_match__in_resource_list(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        for index, res in enumerate(self.test_resources_in_resource_list):
            res.resource_type = ResourceType.objects.get(mimetype='test/b')
            res.save()
        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'resource_assignments': ra
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {'resource_assignments': {self.url(self.test_Dip3): {0: ['The resource type does not match the InputPort']}}}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)




class WorkflowRunSimpleExecutionTest(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_simple_dummy_workflow()
        self.client.force_authenticate(user=self.test_superuser)
        response = self.client.patch("/workflow/{0}/".format(self.test_workflow.uuid), {'valid': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_successful_execution(self):
        ra = self.setUp_resources_for_simple_dummy_workflow()
        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'resource_assignments': ra
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wfrun_id = response.data['uuid']
        wfrun = WorkflowRun.objects.get(uuid=wfrun_id)
        self.assertEqual(wfrun.creator.pk, self.test_superuser.pk)

        dummy_a_runjob = self.dummy_a_wfjob.run_jobs.first()
        dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()

#        self.assertEqual(dummy_a_runjob.status, task_status.SCHEDULED)
#        self.assertEqual(dummy_m_runjob.status, task_status.SCHEDULED)
#        self.assertEqual(WorkflowRun.objects.get(uuid=wfrun_id).status, task_status.SCHEDULED)

#        workflowrun_update = {'status': task_status.REQUEST_PROCESSING}
#        response = self.client.patch("/workflowrun/{0}/".format(str(wfrun_id)), workflowrun_update, format='json')
#        self.assertEqual(response.status_code, status.HTTP_200_OK)

#        dummy_a_runjob = self.dummy_a_wfjob.run_jobs.first()
#        dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()

        # At this point, the automatic RunJob should be finished, and the manual RunJob should wait for input
        self.assertEqual(dummy_a_runjob.status, task_status.FINISHED)
        self.assertEqual(dummy_m_runjob.status, task_status.WAITING_FOR_INPUT)
        self.assertEqual(WorkflowRun.objects.get(uuid=wfrun_id).status, task_status.PROCESSING)

        response = self.client.post("/interactive/{0}/acquire/".format(str(dummy_m_runjob.uuid)))
        assert response.status_code == status.HTTP_200_OK
        user_input = ['any', 'thing']
        response = self.client.post(response.data['working_url'], user_input, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # then manual job should be flagged as finished and should have result
        with open(dummy_m_runjob.outputs.first().resource.resource_file.path) as f:
            self.assertEqual(json.load(f), user_input)
        dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()  # refetch
        self.assertEqual(dummy_m_runjob.status, task_status.FINISHED)
        self.assertEqual(WorkflowRun.objects.get(uuid=wfrun_id).status, task_status.FINISHED)

    def test_automatic_job_fail(self):
        with self.settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=False): # Turn off propagation as task will fail
            ra = self.setUp_resources_for_simple_dummy_workflow()
            self.test_resource.resource_file.save('dummy.txt', ContentFile('will fail'))

            workflowrun_obj = {
                'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
                'resource_assignments': ra
            }

            response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            wfrun_id = response.data['uuid']

#            workflowrun_update = {'status': task_status.REQUEST_PROCESSING}
#            response = self.client.patch("/workflowrun/{0}/".format(str(wfrun_id)), workflowrun_update, format='json')
#            self.assertEqual(response.status_code, status.HTTP_200_OK)

            dummy_a_runjob = self.dummy_a_wfjob.run_jobs.first()
            dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()

            # At this point, the automatic RunJob should fail, and the manual RunJob should not accept input
            self.assertEqual(dummy_a_runjob.status, task_status.FAILED)
            self.assertEqual(dummy_a_runjob.error_summary, 'dummy automatic job error')
            self.assertEqual(dummy_m_runjob.status, task_status.SCHEDULED)
            self.assertEqual(WorkflowRun.objects.get(uuid=wfrun_id).status, task_status.FAILED)

    def test_manual_job_rejected(self):
        ra = self.setUp_resources_for_simple_dummy_workflow()
        self.test_resource.resource_file.save('dummy.txt', ContentFile('dummy text'))

        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'resource_assignments': ra
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wfrun_id = response.data['uuid']

#        workflowrun_update = {'status': task_status.REQUEST_PROCESSING}
#        response = self.client.patch("/workflowrun/{0}/".format(str(wfrun_id)), workflowrun_update, format='json')
#        self.assertEqual(response.status_code, status.HTTP_200_OK)

        dummy_a_runjob = self.dummy_a_wfjob.run_jobs.first()
        dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()

        # At this point, the automatic RunJob should be finished, and the manual RunJob should wait for input
        self.assertEqual(dummy_a_runjob.status, task_status.FINISHED)
        self.assertEqual(dummy_m_runjob.status, task_status.WAITING_FOR_INPUT)

        response = self.client.post("/interactive/{0}/acquire/".format(str(dummy_m_runjob.uuid)))
        assert response.status_code == status.HTTP_200_OK
        user_input = {'fail': 'hahaha'}
        response = self.client.post(response.data['working_url'], user_input)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()  # refetch
        self.assertEqual(dummy_m_runjob.status, task_status.WAITING_FOR_INPUT)
        self.assertEqual(WorkflowRun.objects.get(uuid=wfrun_id).status, task_status.PROCESSING)


    def test_cancel_retry_redo(self):
        ra = self.setUp_resources_for_simple_dummy_workflow()
        self.test_resource.resource_file.save('dummy.txt', ContentFile('dummy text'))

        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'resource_assignments': ra
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wfrun_uuid = response.data['uuid']

        response = self.client.patch("/workflowrun/{0}/".format(wfrun_uuid), {'status': task_status.REQUEST_CANCELLING}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()
        self.assertEqual(dummy_m_runjob.status, task_status.CANCELLED)
        self.assertEqual(WorkflowRun.objects.get(uuid=wfrun_uuid).status, task_status.CANCELLED)

        workflowrun_update = {'status': task_status.PROCESSING}
        response = self.client.patch("/workflowrun/{0}/".format(wfrun_uuid), workflowrun_update, format='json')
        anticipated_message = {"status": ["Invalid status update"]}
        self.assertEqual(anticipated_message, response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(WorkflowRun.objects.get(uuid=wfrun_uuid).status, task_status.CANCELLED)

        workflowrun_update = {'status': task_status.REQUEST_RETRYING}
        response = self.client.patch("/workflowrun/{0}/".format(wfrun_uuid), workflowrun_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()
        self.assertEqual(dummy_m_runjob.status, task_status.WAITING_FOR_INPUT)
        self.assertEqual(WorkflowRun.objects.get(uuid=wfrun_uuid).status, task_status.RETRYING)

        workflowrun_update = {'last_redone_runjob_tree': 'http://localhost:8000/runjob/{0}/'.format(dummy_m_runjob.uuid)}
        response = self.client.patch("/workflowrun/{0}/".format(wfrun_uuid), workflowrun_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()
        self.assertEqual(dummy_m_runjob.status, task_status.WAITING_FOR_INPUT)
        self.assertEqual(WorkflowRun.objects.get(uuid=wfrun_uuid).status, task_status.RETRYING)


    def test_post_cancelled(self):
        ra = self.setUp_resources_for_simple_dummy_workflow()
        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'status': task_status.CANCELLED,
            'resource_assignments': ra
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class WorkflowRunComplexTest(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    "Test workflowrun creation and execution with a complex workflow."
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_complex_dummy_workflow()
        self.client.force_authenticate(user=self.test_superuser)
        response = self.client.patch("/workflow/{0}/".format(self.test_workflow.uuid), {'valid': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_creation(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'resource_assignments': ra
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wfrun_id = response.data['uuid']

        len_rc = len(self.test_resourcecollection)
        self.assertEqual(self.test_wfjob_A.run_jobs.count(), 1)
        self.assertEqual(self.test_wfjob_B.run_jobs.count(), 1)
        self.assertEqual(self.test_wfjob_C.run_jobs.count(), 1)
        self.assertEqual(self.test_wfjob_D.run_jobs.count(), len_rc)
        self.assertEqual(self.test_wfjob_E.run_jobs.count(), len_rc)
        self.assertEqual(self.test_wfjob_F.run_jobs.count(), len_rc)

        self.assertEqual(self.test_Aip.inputs.count(), 1)
        self.assertEqual(self.test_Aop.outputs.count(), 1)
        self.assertEqual(self.test_Bop.outputs.count(), 1)
        self.assertEqual(self.test_Cip1.inputs.count(), 1)
        self.assertEqual(self.test_Cip2.inputs.count(), 1)
        self.assertEqual(self.test_Cop1.outputs.count(), 1)
        self.assertEqual(self.test_Cop2.outputs.count(), 1)
        self.assertEqual(self.test_Dip1.inputs.count(), len_rc)
        self.assertEqual(self.test_Dip2.inputs.count(), len_rc)
        self.assertEqual(self.test_Dop.outputs.count(), len_rc)
        self.assertEqual(self.test_Eip1.inputs.count(), len_rc)
        self.assertEqual(self.test_Eip2.inputs.count(), len_rc)
        self.assertEqual(self.test_Eop.outputs.count(), len_rc)
        self.assertEqual(self.test_Fip1.inputs.count(), len_rc)
        self.assertEqual(self.test_Fip2.inputs.count(), len_rc)
        self.assertEqual(self.test_Fop.outputs.count(), len_rc)

        def same_resources(queryA, queryB):
            return set(queryA.values_list('resource__uuid', flat=True)) == set(queryB.values_list('resource__uuid', flat=True))
        self.assertTrue(same_resources(self.test_Aop.outputs, self.test_Cip1.inputs))
        self.assertTrue(same_resources(self.test_Bop.outputs, self.test_Cip2.inputs))
        self.assertTrue(same_resources(self.test_Cop1.outputs, self.test_Dip2.inputs))
        self.assertTrue(same_resources(self.test_Dop.outputs, self.test_Eip1.inputs))
        self.assertTrue(same_resources(self.test_Dop.outputs, self.test_Fip2.inputs))


        def assert_same_resource_types(op):
            op_types = op.output_port_type.resource_types.all().values_list('mimetype', flat=True)
            for o in op.outputs.all():
                if op.output_port_type.is_list:
                    r = o.resource_list
                    if r.resources.count() > 0:
                        r_type = r.resource_type.mimetype
                        self.assertIn(r_type, op_types)
                else:
                    r = o.resource
                    r_type = r.resource_type.mimetype
                    self.assertIn(r_type, op_types)
        assert_same_resource_types(self.test_Aop)
        assert_same_resource_types(self.test_Bop)
        assert_same_resource_types(self.test_Cop1)
        assert_same_resource_types(self.test_Cop2)
        assert_same_resource_types(self.test_Dop)
        assert_same_resource_types(self.test_Eop)
        assert_same_resource_types(self.test_Fop)


        self.assertEqual(
            set(self.test_Aip.inputs.values_list('resource__uuid', flat=True)),
            set([self.test_resource.uuid])
        )
        self.assertEqual(
            set(self.test_Eip2.inputs.values_list('resource__uuid', flat=True)),
            set([self.test_resource.uuid])
        )
        self.assertEqual(
            set(self.test_Dip3.inputs.values_list('resource_list__uuid', flat=True)),
            set([self.test_resourcelist.uuid])
        )
        self.assertEqual(
            set(self.test_Dip1.inputs.values_list('resource__uuid', flat=True)),
            set(map(lambda res: res.uuid, self.test_resourcecollection))
        )
        self.assertEqual(
            set(self.test_Fip1.inputs.values_list('resource__uuid', flat=True)),
            set(map(lambda res: res.uuid, self.test_resourcecollection))
        )

        # names for resource collection
        rc_names_set = set(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
        Do_names_set = set([])
        for output in self.test_Dop.outputs.all():
            Do_names_set.add(output.resource.name)
        self.assertEqual(rc_names_set, Do_names_set)

        Eo_names_set = set([])
        for output in self.test_Eop.outputs.all():
            Eo_names_set.add(output.resource.name)
        self.assertEqual(rc_names_set, Eo_names_set)

        Fo_names_set = set([])
        for output in self.test_Fop.outputs.all():
            Fo_names_set.add(output.resource_list.name)
        self.assertEqual(rc_names_set, Fo_names_set)

#        self.assertEqual(WorkflowRun.objects.get(uuid=wfrun_id).status, task_status.SCHEDULED)
	self.assertEqual(WorkflowRun.objects.get(uuid=wfrun_id).status, task_status.PROCESSING)

    def test_execution(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        workflowrun_obj = {
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'resource_assignments': ra
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wfrun_id = response.data['uuid']

#        workflowrun_update = {'status': task_status.REQUEST_PROCESSING}
#        response = self.client.patch("/workflowrun/{0}/".format(str(wfrun_id)), workflowrun_update, format='json')
#        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rjA = self.test_wfjob_A.run_jobs.first()
        rjB = self.test_wfjob_B.run_jobs.first()
        rjC = self.test_wfjob_C.run_jobs.first()
        rjDs = self.test_wfjob_D.run_jobs.all()
        rjEs = self.test_wfjob_E.run_jobs.all()
        rjFs = self.test_wfjob_F.run_jobs.all()

        Aout = self.test_Aop.outputs.first()
        Bout = self.test_Bop.outputs.first()
        Cout1 = self.test_Cop1.outputs.first()
        Cout2 = self.test_Cop2.outputs.first()
        Douts = self.test_Dop.outputs.all()
        Eouts = self.test_Eop.outputs.all()
        Fouts = self.test_Fop.outputs.all()

        Ain = self.test_Aip.inputs.first()
        Cin1 = self.test_Cip1.inputs.first()
        Cin2 = self.test_Cip2.inputs.first()
        Din1s = self.test_Dip1.inputs.all()
        Din2s = self.test_Dip2.inputs.all()
        Din3s = self.test_Dip3.inputs.all()
        Ein1s = self.test_Eip1.inputs.all()
        Ein2s = self.test_Eip2.inputs.all()
        Fins = self.test_Eip1.inputs.all()


        self.assertEqual(rjA.status, task_status.FINISHED)
        self.assertEqual(rjB.status, task_status.WAITING_FOR_INPUT)
        self.assertEqual(rjC.status, task_status.SCHEDULED)
        for rjDi in rjDs:
            self.assertEqual(rjDi.status, task_status.SCHEDULED)
        for rjEi in rjEs:
            self.assertEqual(rjEi.status, task_status.SCHEDULED)
        for rjFi in rjFs:
            self.assertEqual(rjFi.status, task_status.SCHEDULED)

        self.assertTrue(Aout.resource.resource_file)
        for r in Bout.resource_list.resources.all():
            self.assertFalse(r.resource_file)
        self.assertFalse(Cout1.resource.resource_file)
        self.assertFalse(Cout2.resource.resource_file)
        for Douti in Douts:
            self.assertFalse(Douti.resource.resource_file)
        for Eouti in Eouts:
            self.assertFalse(Eouti.resource.resource_file)
        for Fouti in Fouts:
            for r in Fouti.resource_list.resources.all():
                self.assertFalse(r.resource_file)


        # Work with RunJob B
        response = self.client.post("/interactive/{0}/acquire/".format(str(rjB.uuid)))
        assert response.status_code == status.HTTP_200_OK
        response = self.client.post(response.data['working_url'], {'foo': 'bar'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ## refetch
        rjA = self.test_wfjob_A.run_jobs.first()
        rjB = self.test_wfjob_B.run_jobs.first()
        rjC = self.test_wfjob_C.run_jobs.first()
        rjDs = self.test_wfjob_D.run_jobs.all()
        rjEs = self.test_wfjob_E.run_jobs.all()
        rjFs = self.test_wfjob_F.run_jobs.all()

        Aout = self.test_Aop.outputs.first()
        Bout = self.test_Bop.outputs.first()
        Cout1 = self.test_Cop1.outputs.first()
        Cout2 = self.test_Cop2.outputs.first()
        Douts = self.test_Dop.outputs.all()
        Eouts = self.test_Eop.outputs.all()
        Fouts = self.test_Fop.outputs.all()

        Ain = self.test_Aip.inputs.first()
        Cin1 = self.test_Cip1.inputs.first()
        Cin2 = self.test_Cip2.inputs.first()
        Din1s = self.test_Dip1.inputs.all()
        Din2s = self.test_Dip2.inputs.all()
        Din3s = self.test_Dip3.inputs.all()
        Ein1s = self.test_Eip1.inputs.all()
        Ein2s = self.test_Eip2.inputs.all()
        Fin1s = self.test_Fip1.inputs.all()
        Fin2s = self.test_Fip2.inputs.all()

        self.assertEqual(rjB.status, task_status.FINISHED)
        self.assertEqual(rjC.status, task_status.FINISHED)
        for rjDi in rjDs:
            self.assertEqual(rjDi.status, task_status.WAITING_FOR_INPUT)
        for rjEi in rjEs:
            self.assertEqual(rjEi.status, task_status.SCHEDULED)
        for rjFi in rjFs:
            self.assertEqual(rjFi.status, task_status.SCHEDULED)

        for r in Bout.resource_list.resources.all():
            self.assertTrue(r.resource_file)
        self.assertTrue(Cout1.resource.resource_file)
        self.assertTrue(Cout2.resource.resource_file)
        for Douti in Douts:
            self.assertFalse(Douti.resource.resource_file)
        for Eouti in Eouts:
            self.assertFalse(Eouti.resource.resource_file)
        for Fouti in Fouts:
            for r in Fouti.resource_list.resources.all():
                self.assertFalse(r.resource_file)

        # Work with one of RunJob D
        response = self.client.post("/interactive/{0}/acquire/".format(str(rjDs[0].uuid)))
        assert response.status_code == status.HTTP_200_OK
        response = self.client.post(response.data['working_url'], {'foo': 'bar'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


        ## refetch
        rjA = self.test_wfjob_A.run_jobs.first()
        rjB = self.test_wfjob_B.run_jobs.first()
        rjC = self.test_wfjob_C.run_jobs.first()
        rjDs = self.test_wfjob_D.run_jobs.all()
        rjEs = self.test_wfjob_E.run_jobs.all()
        rjFs = self.test_wfjob_F.run_jobs.all()

        Aout = self.test_Aop.outputs.first()
        Bout = self.test_Bop.outputs.first()
        Cout1 = self.test_Cop1.outputs.first()
        Cout2 = self.test_Cop2.outputs.first()
        Douts = self.test_Dop.outputs.all()
        Eouts = self.test_Eop.outputs.all()
        Fouts = self.test_Fop.outputs.all()

        Ain = self.test_Aip.inputs.first()
        Cin1 = self.test_Cip1.inputs.first()
        Cin2 = self.test_Cip2.inputs.first()
        Din1s = self.test_Dip1.inputs.all()
        Din2s = self.test_Dip2.inputs.all()
        Din3s = self.test_Dip3.inputs.all()
        Ein1s = self.test_Eip1.inputs.all()
        Ein2s = self.test_Eip2.inputs.all()
        Fin1s = self.test_Fip1.inputs.all()
        Fin2s = self.test_Fip2.inputs.all()

        rjD0 = rjDs[0]
        rjDremain = rjDs[1:]

        Dout0 = rjD0.outputs.get(output_port__output_port_type__name='out_typeA')
        rjE0 = Dout0.resource.inputs.filter(run_job__workflow_job=self.test_wfjob_E)[0].run_job
        Eout0 = rjE0.outputs.get(output_port__output_port_type__name='out_typeA')
        rjF0 = Dout0.resource.inputs.filter(run_job__workflow_job=self.test_wfjob_F)[0].run_job
        Fout0 = rjF0.outputs.get(output_port__output_port_type__name='out_typeL')
        self.assertEqual(rjD0.status, task_status.FINISHED)
        self.assertTrue(Dout0.resource.resource_file)
        self.assertEqual(rjE0.status, task_status.FINISHED)
        self.assertTrue(Eout0.resource.resource_file)
        self.assertEqual(rjF0.status, task_status.FINISHED)
        for r in Fout0.resource_list.resources.all():
            self.assertTrue(r.resource_file)

        for rjDi in rjDremain:
            Douti = rjDi.outputs.get(output_port__output_port_type__name='out_typeA')
            rjEi = Douti.resource.inputs.filter(run_job__workflow_job=self.test_wfjob_E)[0].run_job
            Eouti = rjEi.outputs.get(output_port__output_port_type__name='out_typeA')
            rjFi = Douti.resource.inputs.filter(run_job__workflow_job=self.test_wfjob_F)[0].run_job
            Fouti = rjFi.outputs.get(output_port__output_port_type__name='out_typeL')
            self.assertEqual(rjDi.status, task_status.WAITING_FOR_INPUT)
            self.assertFalse(Douti.resource.resource_file)
            self.assertEqual(rjEi.status, task_status.SCHEDULED)
            self.assertFalse(Eouti.resource.resource_file)
            self.assertEqual(rjFi.status, task_status.SCHEDULED)
            for r in Fouti.resource_list.resources.all():
                self.assertFalse(r.resource_file)

        self.assertEqual(WorkflowRun.objects.get(uuid=wfrun_id).status, task_status.PROCESSING)

        # Work with all Runjob Ds
        for rjDi in rjDremain:
            response = self.client.post("/interactive/{0}/acquire/".format(str(rjDi.uuid)))
            assert response.status_code == status.HTTP_200_OK
            response = self.client.post(response.data['working_url'], {'foo': 'bar'})
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        ## refetch
        rjA = self.test_wfjob_A.run_jobs.first()
        rjB = self.test_wfjob_B.run_jobs.first()
        rjC = self.test_wfjob_C.run_jobs.first()
        rjDs = self.test_wfjob_D.run_jobs.all()
        rjEs = self.test_wfjob_E.run_jobs.all()
        rjFs = self.test_wfjob_F.run_jobs.all()

        Aout = self.test_Aop.outputs.first()
        Bout = self.test_Bop.outputs.first()
        Cout1 = self.test_Cop1.outputs.first()
        Cout2 = self.test_Cop2.outputs.first()
        Douts = self.test_Dop.outputs.all()
        Eouts = self.test_Eop.outputs.all()
        Fouts = self.test_Fop.outputs.all()

        Ain = self.test_Aip.inputs.first()
        Cin1 = self.test_Cip1.inputs.first()
        Cin2 = self.test_Cip2.inputs.first()
        Din1s = self.test_Dip1.inputs.all()
        Din2s = self.test_Dip2.inputs.all()
        Din3s = self.test_Dip3.inputs.all()
        Ein1s = self.test_Eip1.inputs.all()
        Ein2s = self.test_Eip2.inputs.all()
        Fin1s = self.test_Fip1.inputs.all()
        Fin2s = self.test_Fip2.inputs.all()

        for rjDi in rjDs:
            self.assertEqual(rjDi.status, task_status.FINISHED)
        for Douti in Douts:
            self.assertTrue(Douti.resource.resource_file)
        for rjEi in rjEs:
            self.assertEqual(rjEi.status, task_status.FINISHED)
        for Eouti in Eouts:
            self.assertTrue(Eouti.resource.resource_file)
        for rjFi in rjFs:
            self.assertEqual(rjFi.status, task_status.FINISHED)
        for Fouti in Fouts:
            for r in Fouti.resource_list.resources.all():
                self.assertTrue(r.resource_file)

        self.assertEqual(WorkflowRun.objects.get(uuid=wfrun_id).status, task_status.FINISHED)
