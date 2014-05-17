from django.test import TestCase
from django.contrib.auth.models import User
from rodan.models.page import Page
from rodan.models.project import Project


class PageTestCase(TestCase):
    fixtures = ["1_users", "2_initial_data"]

    def setUp(self):
        self.test_user = User.objects.get(username="ahankins")
        self.test_project = Project.objects.get(uuid="9e8e928b4ec24a09b6113f1b0af1ea53")

    def test_save(self):
        page = Page(project=self.test_project, creator=self.test_user, name="test page")
        page.save()

        retr_page = Page.objects.get(name="test page")
        self.assertEqual(retr_page.name, page.name)

    def test_delete(self):
        page = Page(project=self.test_project, creator=self.test_user, name="test page")
        page.save()

        retr_page = Page.objects.get(name="test page")
        retr_page.delete()

        retr_page2 = Page.objects.filter(name="test page")
        self.assertFalse(retr_page2.exists())
