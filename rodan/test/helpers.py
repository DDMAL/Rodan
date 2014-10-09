from model_mommy import mommy
from django.contrib.auth.models import User
from rodan.models import Project, Job
import time

class RodanTestSetUpMixin(object):
    def setUp_user(self):
        self.test_user = User.objects.create_user(username="ahankins", password="hahaha")

    def setUp_basic_workflow(self):
        """
        Workflow Graph:
        test_workflowjob => test_workflowjob2
        """
        self.setUp_user()

        self.test_job = mommy.make('rodan.Job')
        self.test_inputporttype = mommy.make('rodan.InputPortType',
                                             maximum=3,
                                             minimum=1,
                                             job=self.test_job,
                                             resource_type=[0, 1])
        self.test_outputporttype = mommy.make('rodan.OutputPortType',
                                              maximum=3,
                                              minimum=1,
                                              job=self.test_job,
                                              resource_type=[0, 1, 2])

        self.test_project = mommy.make('rodan.Project')
        self.test_workflow = mommy.make('rodan.Workflow', project=self.test_project)
        self.test_resources = mommy.make('rodan.Resource', _quantity=10,
                                         project=self.test_project,
                                         resource_type=0,
                                         processed=True)

        # build this graph: test_workflowjob --> test_workflowjob2
        self.test_workflowjob = mommy.make('rodan.WorkflowJob',
                                           workflow=self.test_workflow,
                                           job=self.test_job)
        inputport = mommy.make('rodan.InputPort',
                               workflow_job=self.test_workflowjob,
                               input_port_type=self.test_inputporttype)
        outputport = mommy.make('rodan.OutputPort',
                                workflow_job=self.test_workflowjob,
                                output_port_type=self.test_outputporttype)
        test_resourceassignment = mommy.make('rodan.ResourceAssignment',
                                             input_port=inputport)
        test_resourceassignment.resources.add(*self.test_resources)


        test_connection = mommy.make('rodan.Connection',
                                     output_port=outputport,
                                     input_port__input_port_type=self.test_inputporttype,
                                     input_port__workflow_job__workflow=self.test_workflow,
                                     input_port__workflow_job__job=self.test_job)
        self.test_workflowjob2 = test_connection.input_port.workflow_job
        outputport2 = mommy.make('rodan.OutputPort',
                                 workflow_job=self.test_workflowjob2,
                                 output_port_type=self.test_outputporttype)

    def setUp_dummy_workflow(self):
        """
        Workflow Graph:
        dummy_a_wfjob => dummy_m_wfjob
        """
        self.setUp_user()

        from rodan.jobs.devel.dummy_job import load_dummy_automatic_job, load_dummy_manual_job
        load_dummy_automatic_job()
        load_dummy_manual_job()
        dummy_a_job = Job.objects.get(job_name='rodan.jobs.devel.dummy_automatic_job')
        dummy_m_job = Job.objects.get(job_name='rodan.jobs.devel.dummy_manual_job')


        self.test_project = mommy.make('rodan.Project')
        self.test_workflow = mommy.make('rodan.Workflow', project=self.test_project)
        self.test_resource = mommy.make('rodan.Resource',
                                        project=self.test_project,
                                        resource_type=0,
                                        processed=True)

        # build this graph: dummy_a_wfjob => dummy_m_wfjob
        self.dummy_a_wfjob = mommy.make('rodan.WorkflowJob',
                                        workflow=self.test_workflow,
                                        job=dummy_a_job)
        inputport_a = mommy.make('rodan.InputPort',
                                 workflow_job=self.dummy_a_wfjob,
                                 input_port_type=dummy_a_job.input_port_types.first())
        outputport_a = mommy.make('rodan.OutputPort',
                                  workflow_job=self.dummy_a_wfjob,
                                  output_port_type=dummy_a_job.output_port_types.first())
        resourceassignment = mommy.make('rodan.ResourceAssignment',
                                        input_port=inputport_a)
        resourceassignment.resources.add(self.test_resource)


        self.dummy_m_wfjob = mommy.make('rodan.WorkflowJob',
                                        workflow=self.test_workflow,
                                        job=dummy_m_job)
        inputport_m = mommy.make('rodan.InputPort',
                                 workflow_job=self.dummy_m_wfjob,
                                 input_port_type=dummy_m_job.input_port_types.first())
        outputport_m = mommy.make('rodan.OutputPort',
                                  workflow_job=self.dummy_m_wfjob,
                                  output_port_type=dummy_m_job.output_port_types.first())

        test_connection = mommy.make('rodan.Connection',
                                     output_port=outputport_a,
                                     input_port=inputport_m)


class RodanTestTearDownMixin(object):
    """
    Please put this mixin on the leftmost place in the parent classes
    to let tearDown() method take effect, like:

        class ProjectViewTestCase(RodanTestTearDownMixin, APITestCase)
    """
    def tearDown(self):
        # tearing this down manually calls the delete method,
        # which cleans up the filesystem
        Project.objects.all().delete()
