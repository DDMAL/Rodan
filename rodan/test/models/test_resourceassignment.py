from django.test import TestCase
from rodan.models.workflow import Workflow
from rodan.models.inputport import InputPort
from rodan.models.resourceassignment import ResourceAssignment
from rodan.models.resource import Resource
from model_mommy import mommy
from rodan.test.helpers import RodanTestTearDownMixin, RodanTestSetUpMixin


class ResourceAssignmentTestCase(RodanTestTearDownMixin, TestCase, RodanTestSetUpMixin):
    pass
