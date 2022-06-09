import unittest
from os import environ

from rodan_connection import RodanConnection

URL = "rodan2.simssa.ca"


class RodanE2ETestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        username = environ["RODAN_USERNAME"]
        password = environ["RODAN_PASSWORD"]
        cls.rodan = RodanConnection(URL, username, password)
        cls.rodan.login_to_rodan()

    def setUp(self):
        self.rodan.navigate_home()
        self.rodan.delete_all_resources("projects")

    def test_create_project(self):
        self.rodan.create_new_project()
        self.assertTrue(self.rodan.get_all_projects())

    def test_create_workflow(self):
        self.rodan.create_new_project()
        project = self.rodan.get_most_recent_project()
        workflow = self.rodan.create_workflow(project)
        self.assertIsNotNone(workflow)
