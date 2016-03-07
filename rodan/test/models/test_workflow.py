from django.test import TestCase
from django.contrib.auth.models import User
from rodan.models import Workflow, Project
from model_mommy import mommy
from rodan.test.helpers import RodanTestTearDownMixin, RodanTestSetUpMixin


class WorkflowTestCase(RodanTestTearDownMixin, TestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.test_project = mommy.make('rodan.Project')
        self.test_user = mommy.make(User)

        self.test_workflow_data = {
            "name": "test workflow",
            "project": self.test_project,
            "creator": self.test_user
        }

    def test_save(self):
        workflow = Workflow(**self.test_workflow_data)
        workflow.save()

        retr_workflow = Workflow.objects.get(name="test workflow")
        self.assertEqual(retr_workflow.name, workflow.name)

    def test_delete(self):
        workflow = Workflow(**self.test_workflow_data)
        workflow.save()

        retr_workflow = Workflow.objects.get(name="test workflow")
        retr_workflow.delete()

        retr_workflow2 = Workflow.objects.filter(name="test workflow")
        self.assertFalse(retr_workflow2.exists())

    def test_should_not_be_valid(self):
        workflow = Workflow(**self.test_workflow_data)
        workflow.save()

        retr_workflow = Workflow.objects.get(name="test workflow")
        self.assertFalse(retr_workflow.valid)


class WorkflowInvalidateTestCase(RodanTestTearDownMixin, TestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_basic_workflow()
        # add a wfj group
        self.test_workflowjobgroup = mommy.make('rodan.WorkflowJobGroup',
                                                workflow=self.test_workflow)
        self.test_workflowjob.group = self.test_workflowjobgroup
        self.test_workflowjob.save()
        # force valid=True
        self.test_workflow.valid = True
        self.test_workflow.save()


    def test_creating_workflowjob_should_invalidate(self):
        wfj3 = mommy.make('rodan.WorkflowJob', workflow=self.test_workflow)
        # Refetch
        wf = Workflow.objects.get(uuid=self.test_workflow.uuid)
        self.assertFalse(wf.valid)
    def test_altering_workflowjob_job_should_invalidate(self):
        self.test_workflowjob.job = mommy.make('rodan.Job')
        self.test_workflowjob.save()
        # Refetch
        wf = Workflow.objects.get(uuid=self.test_workflow.uuid)
        self.assertFalse(wf.valid)
    def test_altering_workflowjob_job_settings_should_invalidate(self):
        self.test_workflowjob.job_settings = {'a': 'a'}
        self.test_workflowjob.save()
        # Refetch
        wf = Workflow.objects.get(uuid=self.test_workflow.uuid)
        self.assertFalse(wf.valid)
    def test_altering_workflowjob_name_should_not_invalidate(self):
        self.test_workflowjob.name = 'my name'
        self.test_workflowjob.save()
        # Refetch
        wf = Workflow.objects.get(uuid=self.test_workflow.uuid)
        self.assertTrue(wf.valid)
    def test_altering_workflowjob_group_should_not_invalidate(self):
        self.test_workflowjob.group = mommy.make('rodan.WorkflowJobGroup',
                                                 workflow=self.test_workflow)
        self.test_workflowjob.save()
        # Refetch
        wf = Workflow.objects.get(uuid=self.test_workflow.uuid)
        self.assertTrue(wf.valid)
    def test_deleting_workflowjob_should_invalidate(self):
        self.test_workflowjob.delete()
        # Refetch
        wf = Workflow.objects.get(uuid=self.test_workflow.uuid)
        self.assertFalse(wf.valid)


    def test_creating_inputport_should_invalidate(self):
        mommy.make('rodan.InputPort',
                   workflow_job=self.test_workflowjob,
                   input_port_type=self.test_inputporttype)
        # Refetch
        wf = Workflow.objects.get(uuid=self.test_workflow.uuid)
        self.assertFalse(wf.valid)
    def test_altering_inputport_workflow_job_should_invalidate(self):
        ip = self.test_workflowjob.input_ports.first()
        ip.workflow_job = mommy.make('rodan.WorkflowJob')
        ip.save()
        # Refetch
        wf = Workflow.objects.get(uuid=self.test_workflow.uuid)
        self.assertFalse(wf.valid)
    def test_altering_inputport_input_port_type_should_invalidate(self):
        ip = self.test_workflowjob.input_ports.first()
        ip.input_port_type = mommy.make('rodan.InputPortType')
        ip.save()
        # Refetch
        wf = Workflow.objects.get(uuid=self.test_workflow.uuid)
        self.assertFalse(wf.valid)
    def test_altering_inputport_label_should_not_invalidate(self):
        ip = self.test_workflowjob.input_ports.first()
        ip.label = "new label"
        ip.save()
        # Refetch
        wf = Workflow.objects.get(uuid=self.test_workflow.uuid)
        self.assertTrue(wf.valid)
    def test_deleting_inputport_should_invalidate(self):
        ip = self.test_workflowjob.input_ports.first()
        ip.delete()
        # Refetch
        wf = Workflow.objects.get(uuid=self.test_workflow.uuid)
        self.assertFalse(wf.valid)


    def test_creating_outputport_should_invalidate(self):
        mommy.make('rodan.OutputPort',
                   workflow_job=self.test_workflowjob,
                   output_port_type=self.test_outputporttype)
        # Refetch
        wf = Workflow.objects.get(uuid=self.test_workflow.uuid)
        self.assertFalse(wf.valid)
    def test_altering_outputport_workflow_job_should_invalidate(self):
        op = self.test_workflowjob2.output_ports.first()
        op.workflow_job = mommy.make('rodan.WorkflowJob')
        op.save()
        # Refetch
        wf = Workflow.objects.get(uuid=self.test_workflow.uuid)
        self.assertFalse(wf.valid)
    def test_altering_outputport_output_port_type_should_invalidate(self):
        op = self.test_workflowjob2.output_ports.first()
        op.output_port_type = mommy.make('rodan.OutputPortType')
        op.save()
        # Refetch
        wf = Workflow.objects.get(uuid=self.test_workflow.uuid)
        self.assertFalse(wf.valid)
    def test_altering_outputport_label_should_not_invalidate(self):
        op = self.test_workflowjob2.output_ports.first()
        op.label = "new label"
        op.save()
        # Refetch
        wf = Workflow.objects.get(uuid=self.test_workflow.uuid)
        self.assertTrue(wf.valid)
    def test_deleting_outputport_should_invalidate(self):
        op = self.test_workflowjob2.output_ports.first()
        op.delete()
        # Refetch
        wf = Workflow.objects.get(uuid=self.test_workflow.uuid)
        self.assertFalse(wf.valid)


    def test_creating_connection_should_invalidate(self):
        op = self.test_workflowjob2.output_ports.first()
        mommy.make('rodan.Connection',
                   output_port=op,
                   input_port__workflow_job__workflow=self.test_workflow)
        # Refetch
        wf = Workflow.objects.get(uuid=self.test_workflow.uuid)
        self.assertFalse(wf.valid)
    def test_altering_connection_input_port_should_invalidate(self):
        conn = self.test_workflowjob.output_ports.first().connections.first()
        conn.input_port = mommy.make('rodan.InputPort')
        conn.save()
        # Refetch
        wf = Workflow.objects.get(uuid=self.test_workflow.uuid)
        self.assertFalse(wf.valid)
    def test_altering_connection_output_port_should_invalidate(self):
        conn = self.test_workflowjob.output_ports.first().connections.first()
        conn.output_port = mommy.make('rodan.OutputPort')
        conn.save()
        # Refetch
        wf = Workflow.objects.get(uuid=self.test_workflow.uuid)
        self.assertFalse(wf.valid)
    def test_deleting_connection_should_invalidate(self):
        conn = self.test_workflowjob.output_ports.first().connections.first()
        conn.delete()
        # Refetch
        wf = Workflow.objects.get(uuid=self.test_workflow.uuid)
        self.assertFalse(wf.valid)


    def test_creating_workflowjobgroup_should_not_invalidate(self):
        wfjg2 = mommy.make('rodan.WorkflowJobGroup',
                           workflow=self.test_workflow)
        self.test_workflowjob2.group = self.test_workflowjobgroup
        self.test_workflowjob2.save()
        # Refetch
        wf = Workflow.objects.get(uuid=self.test_workflow.uuid)
        self.assertTrue(wf.valid)
    def test_deleting_workflowjobgroup_should_not_invalidate(self):
        self.test_workflowjobgroup.delete()
        # Refetch
        wf = Workflow.objects.get(uuid=self.test_workflow.uuid)
        self.assertTrue(wf.valid)


class WorkflowPortsTestCase(RodanTestTearDownMixin, TestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_basic_workflow()
        self.test_ip1 = self.test_workflowjob.input_ports.first()
        self.test_ip2 = self.test_workflowjob2.input_ports.first()
        self.test_op1 = self.test_workflowjob.output_ports.first()
        self.test_op2 = self.test_workflowjob2.output_ports.first()
        self.test_ip1.extern = True
        self.test_ip1.save()
        self.test_op2.extern = True
        self.test_op2.save()

    def test_valid(self):
        self.test_workflow.valid = True
        self.test_workflow.save()

        self.assertEqual(len(self.test_workflow.workflow_input_ports), 1)
        self.assertEqual(self.test_workflow.workflow_input_ports[0], self.test_ip1)

        self.assertEqual(len(self.test_workflow.workflow_output_ports), 1)
        self.assertEqual(self.test_workflow.workflow_output_ports[0], self.test_op2)

    def test_invalid(self):
        self.test_workflow.valid = False
        self.test_workflow.save()
        self.assertEqual(self.test_workflow.workflow_input_ports, [])
        self.assertEqual(self.test_workflow.workflow_output_ports, [])
