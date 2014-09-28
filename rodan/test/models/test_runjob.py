import os
from django.test import TestCase
from rodan.models.workflowrun import WorkflowRun
from rodan.models.workflowjob import WorkflowJob
from rodan.models.runjob import RunJob
from model_mommy import mommy
from rodan.test.RodanTestHelpers import RodanTestTearDownMixin


class RunJobTestCase(RodanTestTearDownMixin, TestCase):
    def setUp(self):
        self.test_workflowjob = mommy.make('rodan.WorkflowJob')
        self.test_workflowrun = mommy.make('rodan.WorkflowRun',
                                           workflow=self.test_workflowjob.workflow)
        self.test_runjob = mommy.make('rodan.RunJob',
                                      workflow_job=self.test_workflowjob,
                                      workflow_run=self.test_workflowrun)

    def test_save(self):
        test_runjob = RunJob(workflow_run=self.test_workflowrun, workflow_job=self.test_workflowjob)
        test_runjob.save()

        # test that the paths were created properly
        rj_path = test_runjob.runjob_path
        self.assertTrue(os.path.exists(rj_path))

        retr_runjob = RunJob.objects.get(uuid=test_runjob.pk)
        self.assertEqual(retr_runjob, test_runjob)
        retr_runjob.delete()

    def test_delete(self):
        test_runjob = self.test_runjob
        rj_path = test_runjob.runjob_path
        test_runjob.delete()
        self.assertFalse(os.path.exists(rj_path))
