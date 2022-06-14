import unittest
import logging
from os import environ

from .rodan_connection import RodanConnection

DEFAULT_URL = "rodan-staging.simssa.ca"


class RodanE2ETestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        username = environ["RODAN_USERNAME"]
        password = environ["RODAN_PASSWORD"]
        url = None
        try:
            url = environ["RODAN_URL"]
        except KeyError:
            print(
                "RODAN_URL not found in environment variables, "
                f"falling back to default: {DEFAULT_URL}"
            )
            url = DEFAULT_URL
        cls.rodan = RodanConnection(url, username, password)
        cls.rodan.navigate_home()
        cls.rodan.login_to_rodan()

    def setUp(self):
        self.rodan.delete_all_resources("projects")
        self.rodan.delete_all_resources("workflows")
        self.rodan.navigate_home()

    def test_create_project(self):
        self.rodan.create_new_project()
        self.assertTrue(self.rodan.get_most_recent_from_table("projects"))

    def test_create_workflow(self):
        self.rodan.create_new_project()
        project = self.rodan.get_most_recent_from_table("projects")
        workflow = self.rodan.create_workflow(project)
        self.assertIsNotNone(workflow)

    def test_build_workflow(self):
        self.rodan.create_new_project()
        project = self.rodan.get_most_recent_from_table("projects")
        workflow = self.rodan.create_workflow(project)
        self.rodan.build_workflow(workflow)

