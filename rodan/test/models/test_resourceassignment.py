from django.test import TestCase
from rodan.models.workflow import Workflow
from rodan.models.inputport import InputPort
from rodan.models.resourceassignment import ResourceAssignment
from rodan.models.resource import Resource
from model_mommy import mommy
from rodan.test.helpers import RodanTestTearDownMixin


class ResourceAssignmentTestCase(RodanTestTearDownMixin, TestCase):
    def setUp(self):
        self.test_inputport = mommy.make('rodan.InputPort')
        self.test_resources = mommy.make('rodan.Resource', _quantity=10,
                                         project=self.test_inputport.workflow_job.workflow.project)

    def test_save(self):
        resource_assignment = ResourceAssignment(input_port=self.test_inputport)
        resource_assignment.save()
        for res in self.test_resources:
            resource_assignment.resources.add(res)
            resource_assignment.save()

        retr_ra = ResourceAssignment.objects.get(input_port__workflow_job__workflow=self.test_inputport.workflow_job.workflow)
        self.assertEqual(retr_ra, resource_assignment)
