from django.test import TestCase
from django.db.models import ProtectedError
from model_bakery import baker
from rodan.test.helpers import RodanTestTearDownMixin, RodanTestSetUpMixin


class ProjectTestCase(RodanTestTearDownMixin, TestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()

    def test_delete_project_with_workflowrun(self):
        return
        prj = baker.make("rodan.Project")
        wfrun = baker.make("rodan.WorkflowRun", project=prj)
        rj = baker.make("rodan.RunJob", workflow_run=wfrun)
        resi = baker.make("rodan.Resource", project=prj)
        reso = baker.make("rodan.Resource", project=prj)
        i = baker.make("rodan.Input", run_job=rj, resource=resi)  # noqa
        o = baker.make("rodan.Output", run_job=rj, resource=reso)
        reso.origin = o
        reso.save()

        wfrun2 = baker.make("rodan.WorkflowRun", project=prj)
        rj2 = baker.make("rodan.RunJob", workflow_run=wfrun2)  # noqa
        reso2 = baker.make("rodan.Resource", project=prj)
        i2 = baker.make("rodan.Input", run_job=rj, resource=reso)  # noqa
        o2 = baker.make("rodan.Output", run_job=rj, resource=reso2)  # noqa
        reso2.origin = o
        reso2.save()

        try:
            prj.delete()
        except ProtectedError as e:
            self.fail("ProtectedError when deleting project: {0}".format(e))
