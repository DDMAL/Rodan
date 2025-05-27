from django.test import TestCase
from django.db.models import ProtectedError
from model_mommy import mommy
from rodan.test.helpers import RodanTestTearDownMixin, RodanTestSetUpMixin


class ProjectTestCase(RodanTestTearDownMixin, TestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()

    def test_delete_project_with_workflowrun(self):
        return
        prj = mommy.make("rodan.Project")
        wfrun = mommy.make("rodan.WorkflowRun", project=prj)
        rj = mommy.make("rodan.RunJob", workflow_run=wfrun)
        resi = mommy.make("rodan.Resource", project=prj)
        reso = mommy.make("rodan.Resource", project=prj)
        i = mommy.make("rodan.Input", run_job=rj, resource=resi)  # noqa
        o = mommy.make("rodan.Output", run_job=rj, resource=reso)
        reso.origin = o
        reso.save()

        wfrun2 = mommy.make("rodan.WorkflowRun", project=prj)
        rj2 = mommy.make("rodan.RunJob", workflow_run=wfrun2)  # noqa
        reso2 = mommy.make("rodan.Resource", project=prj)
        i2 = mommy.make("rodan.Input", run_job=rj, resource=reso)  # noqa
        o2 = mommy.make("rodan.Output", run_job=rj, resource=reso2)  # noqa
        reso2.origin = o
        reso2.save()

        try:
            prj.delete()
        except ProtectedError as e:
            self.fail("ProtectedError when deleting project: {0}".format(e))
