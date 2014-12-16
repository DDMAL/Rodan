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
        self.test_workflow.valid = True
        self.test_workflow.save()

    def test_connection_save(self):
        conn = self.test_workflowjob.output_ports.first().connections.first()
        conn.save()
        self.test_workflow = Workflow.objects.get(uuid=self.test_workflow.uuid) # refetch
        self.assertFalse(self.test_workflow.valid)
    def test_connection_delete(self):
        conn = self.test_workflowjob.output_ports.first().connections.first()
        conn.delete()
        self.test_workflow = Workflow.objects.get(uuid=self.test_workflow.uuid) # refetch
        self.assertFalse(self.test_workflow.valid)
    def test_inputport_save(self):
        ip = self.test_workflowjob.input_ports.first()
        ip.save()
        self.test_workflow = Workflow.objects.get(uuid=self.test_workflow.uuid) # refetch
        self.assertFalse(self.test_workflow.valid)
    def test_inputport_delete(self):
        ip = self.test_workflowjob.input_ports.first()
        ip.delete()
        self.test_workflow = Workflow.objects.get(uuid=self.test_workflow.uuid) # refetch
        self.assertFalse(self.test_workflow.valid)
    def test_outputport_save(self):
        op = self.test_workflowjob2.output_ports.first()
        op.save()
        self.test_workflow = Workflow.objects.get(uuid=self.test_workflow.uuid) # refetch
        self.assertFalse(self.test_workflow.valid)
    def test_outputport_delete(self):
        op = self.test_workflowjob2.output_ports.first()
        op.delete()
        self.test_workflow = Workflow.objects.get(uuid=self.test_workflow.uuid) # refetch
        self.assertFalse(self.test_workflow.valid)
    def test_resourceassignment_save(self):
        ra = self.test_workflowjob.input_ports.first().resource_assignments.first()
        ra.save()
        self.test_workflow = Workflow.objects.get(uuid=self.test_workflow.uuid) # refetch
        self.assertFalse(self.test_workflow.valid)
    def test_resourceassignment_delete(self):
        ra = self.test_workflowjob.input_ports.first().resource_assignments.first()
        ra.delete()
        self.test_workflow = Workflow.objects.get(uuid=self.test_workflow.uuid) # refetch
        self.assertFalse(self.test_workflow.valid)
    def test_resourcecollection_add_resource(self):
        rc = self.test_workflowjob.input_ports.first().resource_assignments.first().resource_collection
        rc.resources.add(mommy.make('rodan.Resource', project=self.test_project))
        self.test_workflow = Workflow.objects.get(uuid=self.test_workflow.uuid) # refetch
        self.assertFalse(self.test_workflow.valid)
    def test_resourcecollection_remove_resource(self):
        rc = self.test_workflowjob.input_ports.first().resource_assignments.first().resource_collection
        res = rc.resources.first()
        rc.resources.remove(res)
        self.test_workflow = Workflow.objects.get(uuid=self.test_workflow.uuid) # refetch
        self.assertFalse(self.test_workflow.valid)
    def test_resourcecollection_clear_resource(self):
        rc = self.test_workflowjob.input_ports.first().resource_assignments.first().resource_collection
        rc.resources.clear()
        self.test_workflow = Workflow.objects.get(uuid=self.test_workflow.uuid) # refetch
        self.assertFalse(self.test_workflow.valid)
    def test_workflowjob_save(self):
        self.test_workflowjob.save()
        self.test_workflow = Workflow.objects.get(uuid=self.test_workflow.uuid) # refetch
        self.assertFalse(self.test_workflow.valid)
    def test_workflowjob_delete(self):
        self.test_workflowjob.delete()
        self.test_workflow = Workflow.objects.get(uuid=self.test_workflow.uuid) # refetch
        self.assertFalse(self.test_workflow.valid)
    # [TODO]: should we allow fields of resource to be modified by user?
    #def test_resource_save(self):
    #    ra = self.test_workflowjob.input_ports.first().resource_assignments.first()
    #    res = ra.resources.first()
    #    res.save()
    #    self.assertFalse(self.test_workflow.valid)
    def test_resource_delete(self):
        rc = self.test_workflowjob.input_ports.first().resource_assignments.first().resource_collection
        res = rc.resources.first()
        res.delete()
        self.test_workflow = Workflow.objects.get(uuid=self.test_workflow.uuid) # refetch
        self.assertFalse(self.test_workflow.valid)
