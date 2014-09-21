from django.test import TestCase
from rodan.models.workflow import Workflow
from rodan.models.inputport import InputPort
from rodan.models.resourceassignment import ResourceAssignment
from rodan.models.resource import Resource


class ResourceAssignmentTestCase(TestCase):
    fixtures = ['1_users', '2_initial_data']

    def setUp(self):
        self.test_inputport = InputPort.objects.get(uuid="dd35645a7a7845c5a72c9a856ccb920e")

        # It is invalid to have two RAs pointing to the same InputPort.
        ResourceAssignment.objects.get(input_port=self.test_inputport).delete()

        self.test_resources = Resource.objects.all()

        self.test_data = {
            "input_port": self.test_inputport,
        }

    def test_save(self):
        resource_assignment = ResourceAssignment(**self.test_data)
        resource_assignment.save()
        for res in self.test_resources:
            resource_assignment.resources.add(res)
            resource_assignment.save()

        retr_ra = ResourceAssignment.objects.get(input_port__workflow_job__workflow=self.test_inputport.workflow_job.workflow)
        self.assertEqual(retr_ra, resource_assignment)
