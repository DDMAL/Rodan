from django.conf import settings
from django.contrib.auth.models import User
from rodan.models import Project, WorkflowJob, Workflow, ResourceAssignment, InputPort, InputPortType, OutputPort, OutputPortType, Resource, Connection, Job, ResourceType

from rest_framework.test import APITestCase
from rest_framework import status

from model_mommy import mommy
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
import uuid

class WorkflowViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    """
        For clarification of some of the more confusing tests (i.e. loop, merging, and branching), see
        https://github.com/DDMAL/Rodan/wiki/Workflow-View-Test
    """

    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_basic_workflow()
        self.client.login(username="ahankins", password="hahaha")

    def _validate(self, workflow_uuid):
        workflow_update = {
            'valid': True,
        }
        return self.client.patch("/workflow/{0}/".format(workflow_uuid), workflow_update, format='json')


    def test_view__workflow_notfound(self):
        response = self._validate(uuid.uuid1().hex)
        anticipated_message = {'message': 'Workflow not found'}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    def test_view__posting_valid(self):
        workflow_obj = {
            'project': 'http://localhost:8000/project/{0}/'.format(self.test_project.uuid),
            'name': "test workflow",
            'valid': True,
        }
        response = self.client.post("/workflows/", workflow_obj, format='json')
        anticipated_message = {'message': "You can't POST a valid workflow - it must be validated through a PATCH request"}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_view__post(self):
        workflow_obj = {
            'project': 'http://localhost:8000/project/{0}/'.format(self.test_project.uuid),
            'name': "test workflow",
            'creator': 'http://localhost:8000/user/{0}/'.format(self.test_user.pk),
            'valid': False,
        }
        response = self.client.post("/workflows/", workflow_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    def test_view__validation_result_valid(self):
        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        retr_workflow = Workflow.objects.get(pk=self.test_workflow.uuid)
        self.assertTrue(retr_workflow.valid)
    def test_view__validation_result_invalid(self):
        test_workflow_no_jobs = mommy.make('rodan.Workflow', project=self.test_project)
        response = self._validate(test_workflow_no_jobs.uuid)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        retr_workflow = Workflow.objects.get(pk=test_workflow_no_jobs.uuid)
        self.assertFalse(retr_workflow.valid)

    def test_workflowjob__no_output(self):
        self.test_workflowjob2.output_ports.all().delete()
        response = self._validate(self.test_workflow.uuid)
        anticipated_message = {'message': 'The WorkflowJob {0} has no OutputPorts'.format(self.test_workflowjob2.uuid)}
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data, anticipated_message)
    def test_workflowjob__inputport_number_not_satisfy(self):
        mommy.make('rodan.Connection', _quantity=10,
                   output_port=self.test_workflowjob.output_ports.all()[0],
                   input_port__workflow_job=self.test_workflowjob2,
                   input_port__input_port_type=self.test_inputporttype)
        response = self._validate(self.test_workflow.uuid)
        anticipated_message = {'message': 'The number of input ports on WorkflowJob {0} did not meet the requirements'.format(self.test_workflowjob2.uuid)}
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data, anticipated_message)
    def test_workflowjob__outputport_number_not_satisfy(self):
        mommy.make('rodan.Connection', _quantity=10,
                   output_port__workflow_job=self.test_workflowjob,
                   output_port__output_port_type=self.test_outputporttype,
                   input_port__workflow_job=self.test_workflowjob2,
                   input_port__input_port_type=self.test_inputporttype)
        response = self._validate(self.test_workflow.uuid)
        anticipated_message = {'message': 'The number of output ports on WorkflowJob {0} did not meet the requirements'.format(self.test_workflowjob.uuid)}
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data, anticipated_message)
    def test_workflowjob__settings_not_satisfy(self):
        # [TODO]
        pass

    def test_input__multiple_resourceassignments(self):
        ip = self.test_workflowjob.input_ports.all()[0]
        ra2 = mommy.make('rodan.ResourceAssignment',
                         input_port=ip)
        ra2.resources.add(*self.test_resources)
        response = self._validate(self.test_workflow.uuid)
        anticipated_message = {'message': 'InputPort {0} has more than one Connection or ResourceAssignment'.format(ip.uuid)}
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data, anticipated_message)
    def test_input__multiple_connections(self):
        ip = self.test_workflowjob2.input_ports.all()[0]
        mommy.make('rodan.Connection',
                   output_port=self.test_workflowjob.output_ports.all()[0],
                   input_port=ip)
        response = self._validate(self.test_workflow.uuid)
        anticipated_message = {'message': 'InputPort {0} has more than one Connection or ResourceAssignment'.format(ip.uuid)}
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data, anticipated_message)
    def test_input__resourceassignment_and_connection(self):
        ip = self.test_workflowjob2.input_ports.all()[0]
        ra = mommy.make('rodan.ResourceAssignment',
                         input_port=ip)
        ra.resources.add(*self.test_resources)
        response = self._validate(self.test_workflow.uuid)
        anticipated_message = {'message': 'InputPort {0} has more than one Connection or ResourceAssignment'.format(ip.uuid)}
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data, anticipated_message)

    def test_connection__resource_type_not_agree(self):
        job = mommy.make('rodan.Job')
        ipt = mommy.make('rodan.InputPortType',
                         maximum=1,
                         minimum=1,
                         job=job)
        ipt.resource_types.add(*ResourceType.list('mei'))
        conn = mommy.make('rodan.Connection',
                          output_port=self.test_workflowjob2.output_ports.all()[0],
                          input_port__workflow_job__job=job,
                          input_port__workflow_job__workflow=self.test_workflow,
                          input_port__input_port_type=ipt)
        mommy.make('rodan.OutputPort',
                   workflow_job=conn.input_port.workflow_job,
                   output_port_type=self.test_outputporttype)
        response = self._validate(self.test_workflow.uuid)
        anticipated_message = {'message': 'The resource type of OutputPort {0} does not agree with connected InputPort {1}'.format(conn.output_port.uuid, conn.input_port.uuid)}
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data, anticipated_message)

    def test_resourceassignment__resource_not_in_project(self):
        project = mommy.make('rodan.Project')
        resource = mommy.make('rodan.Resource',
                              project=project,  # != self.project
                              compat_resource_file="dummy")
        ra = self.test_workflowjob.input_ports.all()[0].resource_assignments.all()[0]
        ra.resources.add(resource)
        response = self._validate(self.test_workflow.uuid)
        anticipated_message = {'message': 'The resource {0} is not in the project'.format(resource.uuid)}
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data, anticipated_message)
    def test_resourceassignment__resource_null_compat_resource_file(self):
        resource = mommy.make('rodan.Resource',
                              project=self.test_project)
        ra = self.test_workflowjob.input_ports.all()[0].resource_assignments.all()[0]
        ra.resources.add(resource)
        response = self._validate(self.test_workflow.uuid)
        anticipated_message = {'message': 'The compatible resource file of resource {0} is not ready'.format(resource.uuid)}
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data, anticipated_message)
    def test_resourceassignment__no_resources(self):
        ra = self.test_workflowjob.input_ports.all()[0].resource_assignments.all()[0]
        ra.resources.clear()
        response = self._validate(self.test_workflow.uuid)
        anticipated_message = {'message': 'No resource assigned by ResourceAssignment {0}'.format(ra.uuid)}
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data, anticipated_message)
    def test_resourceassignment__resource_type_not_agree(self):
        ra = self.test_workflowjob.input_ports.all()[0].resource_assignments.all()[0]
        res = mommy.make('rodan.Resource',
                         project=self.test_project,
                         compat_resource_file="dummy")
        res.resource_types.add(*ResourceType.list('mei'))
        ra.resources.add(res)


        response = self._validate(self.test_workflow.uuid)
        anticipated_message = {'message': 'The type of resource {0} assigned does not agree with InputPort {1}'.format(res.uuid, ra.input_port.uuid)}
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data, anticipated_message)

    def test_multiple_resource_collections(self):
        test_resourceassignment2 = mommy.make('rodan.ResourceAssignment',
                                              input_port__workflow_job=self.test_workflowjob2,
                                              input_port__input_port_type=self.test_inputporttype)
        test_resourceassignment2.resources.add(*self.test_resources)

        response = self._validate(self.test_workflow.uuid)
        anticipated_message = {'message': 'Multiple resource assignment collections found'}
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data, anticipated_message)

    def test_graph__empty(self):
        test_workflow_no_jobs = mommy.make('rodan.Workflow', project=self.test_project)
        response = self._validate(test_workflow_no_jobs.uuid)
        anticipated_message = {'message': 'No WorkflowJobs in Workflow'}
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data, anticipated_message)
    def test_graph__not_connected(self):
        workflowjob = mommy.make('rodan.WorkflowJob',
                                 workflow=self.test_workflow,
                                 job=self.test_job)
        inputport = mommy.make('rodan.InputPort',
                               workflow_job=workflowjob,
                               input_port_type=self.test_inputporttype)
        outputport = mommy.make('rodan.OutputPort',
                                workflow_job=workflowjob,
                                output_port_type=self.test_outputporttype)
        test_resourceassignment = mommy.make('rodan.ResourceAssignment',
                                             input_port=inputport)
        test_resourceassignment.resources.add(self.test_resources[0])

        test_connection = mommy.make('rodan.Connection',
                                     output_port=outputport,
                                     input_port__input_port_type=self.test_inputporttype,
                                     input_port__workflow_job__workflow=self.test_workflow,
                                     input_port__workflow_job__job=self.test_job)
        test_workflowjob2 = test_connection.input_port.workflow_job
        outputport2 = mommy.make('rodan.OutputPort',
                                 workflow_job=test_workflowjob2,
                                 output_port_type=self.test_outputporttype)

        response = self._validate(self.test_workflow.uuid)
        anticipated_message = {'message': 'Workflow is not connected'}
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data, anticipated_message)
    def test_graph__loop(self):
        mommy.make('rodan.Connection',
                   input_port__input_port_type=self.test_inputporttype,
                   input_port__workflow_job=self.test_workflowjob,
                   output_port__output_port_type=self.test_outputporttype,
                   output_port__workflow_job=self.test_workflowjob2)

        response = self._validate(self.test_workflow.uuid)
        anticipated_message = {'message': 'There appears to be a loop in the workflow'}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
    def test_graph__merging_workflow(self):
        test_no_input_workflowjob = mommy.make('rodan.WorkflowJob',
                                               workflow=self.test_workflow)
        mommy.make('rodan.Connection',
                   output_port__workflow_job=test_no_input_workflowjob,
                   output_port__output_port_type=self.test_outputporttype,
                   input_port__workflow_job=self.test_workflowjob2,
                   input_port__input_port_type=self.test_inputporttype)

        test_connection3 = mommy.make('rodan.Connection',
                                      output_port=self.test_workflowjob2.output_ports.all()[0],
                                      input_port__input_port_type=self.test_inputporttype,
                                      input_port__workflow_job__workflow=self.test_workflow)
        self.test_workflowjob3 = test_connection3.input_port.workflow_job
        mommy.make('rodan.OutputPort',
                   workflow_job=self.test_workflowjob3,
                   output_port_type=self.test_outputporttype)


        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_graph__branching_workflow(self):
        test_connection3 = mommy.make('rodan.Connection',
                                      output_port__output_port_type=self.test_outputporttype,
                                      output_port__workflow_job=self.test_workflowjob2,
                                      input_port__input_port_type=self.test_inputporttype,
                                      input_port__workflow_job__workflow=self.test_workflow)
        self.test_workflowjob3 = test_connection3.input_port.workflow_job
        mommy.make('rodan.OutputPort',
                   workflow_job=self.test_workflowjob3,
                   output_port_type=self.test_outputporttype)

        test_connection2 = mommy.make('rodan.Connection',
                                      output_port__output_port_type=self.test_outputporttype,
                                      output_port__workflow_job=self.test_workflowjob2,
                                      input_port__input_port_type=self.test_inputporttype,
                                      input_port__workflow_job__workflow=self.test_workflow)
        self.test_second_output_workflowjob = test_connection2.input_port.workflow_job
        mommy.make('rodan.OutputPort',
                   workflow_job=self.test_second_output_workflowjob,
                   output_port_type=self.test_outputporttype)

        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
