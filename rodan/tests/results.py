
from django.utils import unittest
from rodan.models.results import Result, Parameter, ResultFile
from rodan.models.projects import JobItem, RodanUser, Page

class TestResult(unittest.TestCase):
    def setUp(self):
        self.ji = JobItem.objects.get(pk=1)
        self.user = RodanUser.objects.get(pk=1)
        self.page = Page.objects.get(pk=1)
        self.result = Result(job_item=self.ji, user=self.user, page=self.page)
        self.result.save()

    def testSaveParams(self):
        params = {"param1": "v1",
                  "param2": "v2"
                 }
        self.result.save_parameters(**params)
        savedParams = self.result.parameter_set.all()

        self.assertEqual(2, len(savedParams))
        # Because params are unordered, we don't know how they're
        # saved. Just check generally
        self.assertTrue(savedParams[0].key in ["param1", "param2"])
        self.assertTrue(savedParams[0].value in ["v1", "v2"])

