from model_mommy import mommy
from django.contrib.auth.models import User
from rodan.models.project import Project


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
