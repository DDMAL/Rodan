from django.test import TestCase
from django.contrib.auth.models import User
from rodan.models import Resource, ResourceLabel, ResourceType
from model_mommy import mommy
from rodan.test.helpers import RodanTestTearDownMixin, RodanTestSetUpMixin


class ResourceLabelTestCase(RodanTestTearDownMixin, TestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.test_user = mommy.make(User)
        self.test_project = mommy.make("rodan.Project")

        self.test_resource = Resource(
            project=self.test_project,
            creator=self.test_user,
            name="testresource.txt",
            resource_type=ResourceType.objects.get(mimetype="test/a1")
        )
        self.test_resource.save()

        self.test_label = ResourceLabel(name="test label")
        self.test_label.save()

    def test_add_label(self):
        self.assertEqual(self.test_resource.labels.count(), 0)
        with self.assertRaises(ResourceLabel.DoesNotExist):
            self.test_resource.labels.get(name="test label")
        self.test_resource.labels.add(self.test_label)
        self.assertEqual(self.test_resource.labels.count(), 1)
        self.assertEqual(
            self.test_resource.labels.get(name="test label").uuid,
            self.test_label.uuid
        )
