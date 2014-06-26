import os
from django.conf import settings
from django.contrib.auth.models import User

from rodan.models.project import Project
from rodan.models.workflowjob import WorkflowJob
from rodan.models.workflow import Workflow
from rodan.models.resourceassignment import ResourceAssignment
from rodan.models.inputport import InputPort
from rodan.models.inputporttype import InputPortType
from rodan.models.outputport import OutputPort
from rodan.models.outputporttype import OutputPortType
from rodan.models.resource import Resource
from rodan.models.connection import Connection
from rodan.models.job import Job

from rest_framework.test import APITestCase
from rest_framework import status


class WorkflowViewTestCase(APITestCase):
    """
        For clarification of some of the more confusing tests (i.e. loop, merging, branching), see
        https://github.com/DDMAL/Rodan/wiki/Workflow-View-Test
    """
    fixtures = ["1_users", "2_initial_data"]

    def setUp(self):
        self.media_root = os.path.join(settings.PROJECT_DIR)

        self.client.login(username="ahankins", password="hahaha")
        self.test_user = User.objects.get(username="ahankins")
        self.test_workflow = Workflow.objects.get(uuid="ff78a1aa79554abcb5f1b0ac7bba2bad")
        self.test_project = Project.objects.get(uuid="9e8e928b4ec24a09b6113f1b0af1ea53")
        self.test_inputport = InputPort.objects.get(uuid="dd35645a7a7845c5a72c9a856ccb920e")
        self.test_workflowjob = WorkflowJob.objects.get(uuid="1e5d20a84d0f46cab47a2389a566ea06")
        self.test_resources = Resource.objects.filter(workflow=self.test_workflow)
        self.test_resourceassignment = ResourceAssignment.objects.get(uuid="cfda287923344720bfbec39081819617")
        self.test_job = Job.objects.get(uuid="a01a8cb0fea143238946d3d344b65790")

    def test_no_workflow_found(self):
        workflow_update = {
            'valid': True,
        }
        response = self.client.patch("/workflow/37d3275809884b61a58a987e6f44821d/", workflow_update, format='json')
        anticipated_message = {'message': 'Workflow not found'}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_validate_no_workflowjobs(self):
        test_project = Project.objects.get(uuid="9e8e928b4ec24a09b6113f1b0af1ea53")

        test_workflow_no_jobs = Workflow(name="no job workflow", project=test_project, creator=self.test_user)
        test_workflow_no_jobs.save()

        workflow_update = {
            'valid': True,
        }
        response = self.client.patch("/workflow/{0}/".format(test_workflow_no_jobs.uuid), workflow_update, format='json')
        anticipated_message = {'message': 'No WorkflowJobs in Workflow'}
        retr_workflow = Workflow.objects.get(pk=test_workflow_no_jobs.uuid)
        self.assertEqual(response.data, anticipated_message)
        self.assertFalse(retr_workflow.valid)

    def test_validate_multiple_resource_collections(self):
        test_resourceassignment2 = ResourceAssignment(input_port=self.test_inputport, workflow=self.test_workflow)
        test_resourceassignment2.save()
        for res in self.test_resources:
            test_resourceassignment2.resources.add(res)

        workflow_update = {
            'valid': True,
        }

        response = self.client.patch("/workflow/ff78a1aa79554abcb5f1b0ac7bba2bad/", workflow_update, format='json')
        anticipated_message = {'message': 'Multiple resource assignment collections found'}
        retr_workflow = Workflow.objects.get(pk="ff78a1aa79554abcb5f1b0ac7bba2bad")
        self.assertEqual(response.data, anticipated_message)
        self.assertFalse(retr_workflow.valid)

    def test_no_posting_valid(self):
        workflow_obj = {
            'project': 'http://localhost:8000/project/9e8e928b4ec24a09b6113f1b0af1ea53/',
            'name': "test workflow",
            'creator': 'http://localhost:8000/user/1/',
            'valid': True,
        }
        response = self.client.post("/workflows/", workflow_obj, format='json')
        anticipated_message = {'message': "You can't POST a valid workflow - it must be validated through a PATCH request"}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post(self):
        workflow_obj = {
            'project': 'http://localhost:8000/project/9e8e928b4ec24a09b6113f1b0af1ea53/',
            'name': "test workflow",
            'creator': 'http://localhost:8000/user/1/',
            'valid': False,
        }
        response = self.client.post("/workflows/", workflow_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_validate_resources_not_in_workflow(self):
        test_orphan_resource = Resource.objects.get(pk="8aa7e270b1c54be49dde5a682b16cda7")
        test_resourceassignment2 = ResourceAssignment(input_port=self.test_inputport, workflow=self.test_workflow)
        test_resourceassignment2.save()
        test_resourceassignment2.resources.add(test_orphan_resource)

        workflow_update = {
            'valid': True,
        }
        response = self.client.patch("/workflow/ff78a1aa79554abcb5f1b0ac7bba2bad/", workflow_update, format='json')
        anticipated_message = {'message': 'The resource {0} is not in the workflow'.format(test_orphan_resource.name)}
        retr_workflow = Workflow.objects.get(pk="ff78a1aa79554abcb5f1b0ac7bba2bad")
        self.assertEqual(response.data, anticipated_message)
        self.assertFalse(retr_workflow.valid)

    def test_loop(self):
        test_outputport = OutputPort.objects.get(label="Test OutputPort II")

        test_workflowjob2 = WorkflowJob.objects.get(uuid="a21f510a16c24701ac0e435b3f4c20f3")

        connection2_data = {
            'input_port': self.test_inputport,
            'input_workflow_job': self.test_workflowjob,
            'output_port': test_outputport,
            'output_workflow_job': test_workflowjob2,
            'workflow': self.test_workflow,
        }
        test_connection2 = Connection(**connection2_data)
        test_connection2.save()

        workflow_update = {
            'valid': True,
        }
        response = self.client.patch("/workflow/ff78a1aa79554abcb5f1b0ac7bba2bad/", workflow_update, format='json')
        anticipated_message = {'message': 'There appears to be a loop in the workflow'}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_merging_workflow(self):
        test_no_input_workflowjob = WorkflowJob(workflow=self.test_workflow, job=self.test_job)
        test_no_input_workflowjob.save()

        test_outputporttype = OutputPortType.objects.get(uuid="1cdb067e98194da48dd3dfa35e84671c")
        test_outputport = OutputPort(workflow_job=test_no_input_workflowjob, output_port_type=test_outputporttype)
        test_outputport.save()

        test_workflowjob2 = WorkflowJob.objects.get(uuid="a21f510a16c24701ac0e435b3f4c20f3")

        test_inputporttype = InputPortType.objects.get(uuid="30ed42546fe440a181f64a2ebdea82e1")
        test_second_inputport = InputPort(workflow_job=test_workflowjob2, input_port_type=test_inputporttype)
        test_second_inputport.save()

        connection2_data = {
            'input_port': test_second_inputport,
            'input_workflow_job': test_workflowjob2,
            'output_port': test_outputport,
            'output_workflow_job': test_no_input_workflowjob,
            'workflow': self.test_workflow,
        }
        test_connection2 = Connection(**connection2_data)
        test_connection2.save()

        test_workflowjob3 = WorkflowJob(workflow=self.test_workflow, job=self.test_job)
        test_workflowjob3.save()

        test_inputport_for_workflowjob3 = InputPort(workflow_job=test_workflowjob3, input_port_type=test_inputporttype)
        test_inputport_for_workflowjob3.save()

        test_outputport_for_workflowjob3 = OutputPort(workflow_job=test_workflowjob3, output_port_type=test_outputporttype)
        test_outputport_for_workflowjob3.save()

        connection3_data = {
            'input_port': test_inputport_for_workflowjob3,
            'input_workflow_job': test_workflowjob3,
            'output_port': OutputPort.objects.get(uuid="0e8b037c44f74364a60a7f5cc397a48d"),
            'output_workflow_job': test_workflowjob2,
            'workflow': self.test_workflow,
        }
        test_connection3 = Connection(**connection3_data)
        test_connection3.save()

        workflow_update = {
            'valid': True,
        }
        response = self.client.patch("/workflow/ff78a1aa79554abcb5f1b0ac7bba2bad/", workflow_update, format='json')
        retr_workflow = Workflow.objects.get(uuid="ff78a1aa79554abcb5f1b0ac7bba2bad")
        self.assertTrue(retr_workflow.valid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_branching_workflow(self):
        test_second_output_workflowjob = WorkflowJob(workflow=self.test_workflow, job=self.test_job)
        test_second_output_workflowjob.save()

        test_workflowjob2 = WorkflowJob.objects.get(uuid="a21f510a16c24701ac0e435b3f4c20f3")

        test_outputporttype = OutputPortType.objects.get(uuid="1cdb067e98194da48dd3dfa35e84671c")
        test_outputport = OutputPort(workflow_job=test_workflowjob2, output_port_type=test_outputporttype)
        test_outputport.save()

        test_workflowjob3 = WorkflowJob(workflow=self.test_workflow, job=self.test_job)
        test_workflowjob3.save()

        test_inputporttype = InputPortType.objects.get(uuid="30ed42546fe440a181f64a2ebdea82e1")
        test_inputport_for_workflowjob3 = InputPort(workflow_job=test_workflowjob3, input_port_type=test_inputporttype)
        test_inputport_for_workflowjob3.save()

        test_second_inputport = InputPort(workflow_job=test_second_output_workflowjob, input_port_type=test_inputporttype)
        test_second_inputport.save()

        test_end_output_port = OutputPort(workflow_job=test_second_output_workflowjob, output_port_type=test_outputporttype)
        test_end_output_port.save()

        test_outputport_for_workflowjob3 = OutputPort(workflow_job=test_workflowjob3, output_port_type=test_outputporttype)
        test_outputport_for_workflowjob3.save()

        connection2_data = {
            'input_port': test_second_inputport,
            'input_workflow_job': test_second_output_workflowjob,
            'output_port': test_outputport,
            'output_workflow_job': test_workflowjob2,
            'workflow': self.test_workflow,
        }
        test_connection2 = Connection(**connection2_data)
        test_connection2.save()

        connection3_data = {
            'input_port': test_inputport_for_workflowjob3,
            'input_workflow_job': test_workflowjob3,
            'output_port': OutputPort.objects.get(uuid="0e8b037c44f74364a60a7f5cc397a48d"),
            'output_workflow_job': test_workflowjob2,
            'workflow': self.test_workflow,
        }
        test_connection3 = Connection(**connection3_data)
        test_connection3.save()

        workflow_update = {
            'valid': True,
        }
        response = self.client.patch("/workflow/ff78a1aa79554abcb5f1b0ac7bba2bad/", workflow_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_outputport_workflow_job(self):
        test_invalid_workflowjob = WorkflowJob(workflow=self.test_workflow, job=self.test_job)
        test_invalid_workflowjob.save()

        test_inputporttype = InputPortType.objects.get(uuid="30ed42546fe440a181f64a2ebdea82e1")
        test_inputport = InputPort(workflow_job=test_invalid_workflowjob, input_port_type=test_inputporttype)
        test_inputport.save()

        connection_data = {
            'input_port': test_inputport,
            'input_workflow_job': test_invalid_workflowjob,
            'output_port': OutputPort.objects.get(uuid="bbdd13ddf05844aa8549e93e82ae4fd2"),
            'output_workflow_job': WorkflowJob.objects.get(uuid="1e5d20a84d0f46cab47a2389a566ea06"),
            'workflow': self.test_workflow,
        }
        test_connection = Connection(**connection_data)
        test_connection.save()

        workflow_update = {
            'valid': True,
        }
        response = self.client.patch("/workflow/ff78a1aa79554abcb5f1b0ac7bba2bad/", workflow_update, format='json')
        anticipated_message = {'message': 'The WorkflowJob {0} has no OutputPorts'.format(test_invalid_workflowjob.uuid)}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_meeting_inputport_requirements(self):
        test_job_with_requirements = Job.objects.get(uuid="76753dd66e1147bcbd6321d749518da2")
        test_job_with_requirements.save()

        test_invalid_workflowjob = WorkflowJob(workflow=self.test_workflow, job=test_job_with_requirements)
        test_invalid_workflowjob.save()

        test_outputporttype = OutputPortType.objects.get(uuid="1cdb067e98194da48dd3dfa35e84671c")
        test_outputport = OutputPort(workflow_job=test_invalid_workflowjob, output_port_type=test_outputporttype)
        test_outputport.save()

        connection_data = {
            'input_port': InputPort.objects.get(uuid="dd35645a7a7845c5a72c9a856ccb920e"),
            'input_workflow_job': WorkflowJob.objects.get(uuid="1e5d20a84d0f46cab47a2389a566ea06"),
            'output_port': test_outputport,
            'output_workflow_job': test_invalid_workflowjob,
            'workflow': self.test_workflow,
        }
        test_connection = Connection(**connection_data)
        test_connection.save()

        workflow_update = {
            'valid': True,
        }
        response = self.client.patch("/workflow/ff78a1aa79554abcb5f1b0ac7bba2bad/", workflow_update, format='json')
        anticipated_message = {'message': 'The number of input ports on WorkflowJob {0} did not meet the requirements'.format(test_invalid_workflowjob.uuid)}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_orphan_in_workfow(self):
        test_orphan_workflowjob = WorkflowJob(workflow=self.test_workflow, job=self.test_job)
        test_orphan_workflowjob.save()

        test_outputporttype = OutputPortType.objects.get(uuid="1cdb067e98194da48dd3dfa35e84671c")
        test_outputport = OutputPort(workflow_job=test_orphan_workflowjob, output_port_type=test_outputporttype)
        test_outputport.save()

        workflow_update = {
            'valid': True,
        }
        response = self.client.patch("/workflow/ff78a1aa79554abcb5f1b0ac7bba2bad/", workflow_update, format='json')
        anticipated_message = {'message': 'The WorkflowJob with ID {0} is not connected to the rest of the workflow'.format(test_orphan_workflowjob.uuid)}
        self.assertEqual(anticipated_message, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
