import os
from django.test import TestCase
from rodan.models.workflowrun import WorkflowRun
from rodan.models.workflowjob import WorkflowJob
from rodan.models.page import Page
from rodan.models.runjob import RunJob


class RunJobTestCase(TestCase):
    fixtures = ["1_users", "2_initial_data"]

    def setUp(self):
        self.test_workflowrun = WorkflowRun.objects.get(uuid="eb4b3661be2a44908c4c932b0783bb3e")
        self.test_workflowjob = WorkflowJob.objects.get(uuid="a21f510a16c24701ac0e435b3f4c20f2")

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
        test_runjob = RunJob.objects.get(uuid="3d558414db10427d82efdd9b9cb985bf")
        rj_path = test_runjob.runjob_path
        test_runjob.delete()
        self.assertFalse(os.path.exists(rj_path))
