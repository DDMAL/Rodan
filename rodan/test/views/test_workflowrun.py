import os
from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

from rodan.models.workflowrun import WorkflowRun
from rodan.models.workflow import Workflow
from rodan.models.runjob import RunJobStatus
from rodan.models.workflowjob import WorkflowJob
from rodan.models.inputport import InputPort
from rodan.models.inputporttype import InputPortType
from rodan.models.outputport import OutputPort
from rodan.models.outputporttype import OutputPortType
from rodan.models.connection import Connection
from rodan.models.job import Job
from rodan.models.runjob import RunJob
from rodan.views.workflowrun import WorkflowRunList
from model_mommy import mommy
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
import uuid
from django.core.files.base import ContentFile
from rodan.models.resource import upload_path

class WorkflowRunViewTest(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_simple_dummy_workflow()
        self.client.login(username="ahankins", password="hahaha")
        response = self.client.patch("/workflow/{0}/".format(self.test_workflow.uuid), {'valid': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list(self):
        response = self.client.get("/workflowruns/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_no_workflow_ID(self):
        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/{0}/'.format(self.test_user.pk)
        }

        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {"message": "You must specify a workflow ID"}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_no_existing_workflow(self):
        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/{0}/'.format(self.test_user.pk),
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(uuid.uuid1()),
        }

        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {"message": "You must specify an existing workflow"}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_not_found(self):
        workflowrun_update = {'cancelled': True}
        response = self.client.patch("/workflowrun/{0}/".format(uuid.uuid1()), workflowrun_update, format='json')
        anticipated_message = {'message': 'Workflow_run not found'}
        self.assertEqual(anticipated_message, response.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



class WorkflowRunSimpleExecutionTest(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_simple_dummy_workflow()
        self.client.login(username="ahankins", password="hahaha")
        response = self.client.patch("/workflow/{0}/".format(self.test_workflow.uuid), {'valid': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_successful_execution(self):
        self.test_resource.compat_resource_file.save('dummy.txt', ContentFile('dummy text'))

        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/{0}/'.format(self.test_user.pk),
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        dummy_a_runjob = self.dummy_a_wfjob.run_jobs.first()
        dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()

        # At this point, the automatic RunJob should be finished, and the manual RunJob should accept input
        self.assertEqual(dummy_a_runjob.status, RunJobStatus.HAS_FINISHED)
        self.assertEqual(dummy_m_runjob.status, RunJobStatus.NOT_RUNNING)
        self.assertEqual(dummy_m_runjob.ready_for_input, True)

        response = self.client.post("/interactive/poly_mask/", {'run_job_uuid': str(dummy_m_runjob.uuid)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # then the workflowrun should re-run
        dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()  # refetch
        self.assertEqual(dummy_m_runjob.status, RunJobStatus.HAS_FINISHED)

    def test_failed_execution(self):
        with self.settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=False): # Turn off propagation as task will fail
            self.test_resource.compat_resource_file.save('dummy.txt', ContentFile('will fail'))
            workflowrun_obj = {
                'creator': 'http://localhost:8000/user/{0}/'.format(self.test_user.pk),
                'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            }

            response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            dummy_a_runjob = self.dummy_a_wfjob.run_jobs.first()
            dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()

            # At this point, the automatic RunJob should fail, and the manual RunJob should not accept input
            self.assertEqual(dummy_a_runjob.status, RunJobStatus.FAILED)
            self.assertEqual(dummy_a_runjob.error_summary, 'dummy automatic job error')
            self.assertEqual(dummy_m_runjob.status, RunJobStatus.NOT_RUNNING)
            self.assertEqual(dummy_m_runjob.ready_for_input, False)

    def test_cancel(self):
        self.test_resource.compat_resource_file.save('dummy.txt', ContentFile('dummy text'))
        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/{0}/'.format(self.test_user.pk),
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wfrun_uuid = response.data['uuid']

        response = self.client.patch("/workflowrun/{0}/".format(wfrun_uuid), {'cancelled': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()
        self.assertEqual(dummy_m_runjob.status, RunJobStatus.CANCELLED)

        workflowrun_update = {'cancelled': False}
        response = self.client.patch("/workflowrun/{0}/".format(wfrun_uuid), workflowrun_update, format='json')
        anticipated_message = {"message": "Workflowrun cannot be uncancelled."}
        self.assertEqual(anticipated_message, response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_cancelled(self):
        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/{0}/'.format(self.test_user.pk),
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
            'cancelled': True
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class WorkflowRunComplexTest(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    "Test workflowrun creation and execution with a complex workflow."
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_complex_dummy_workflow()
        self.client.login(username="ahankins", password="hahaha")
        response = self.client.patch("/workflow/{0}/".format(self.test_workflow.uuid), {'valid': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_creation(self):
        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/{0}/'.format(self.test_user.pk),
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')

        len_rc = len(self.test_resourcecollection)
        self.assertEqual(self.test_wfjob_A.run_jobs.count(), 1)
        self.assertEqual(self.test_wfjob_B.run_jobs.count(), 1)
        self.assertEqual(self.test_wfjob_C.run_jobs.count(), 1)
        self.assertEqual(self.test_wfjob_D.run_jobs.count(), len_rc)
        self.assertEqual(self.test_wfjob_E.run_jobs.count(), len_rc)

        self.assertEqual(self.test_Aip.inputs.count(), 1)
        self.assertEqual(self.test_Aop.outputs.count(), 1)
        self.assertEqual(self.test_Bop.outputs.count(), 1)
        self.assertEqual(self.test_Cip1.inputs.count(), 1)
        self.assertEqual(self.test_Cip2.inputs.count(), 1)
        self.assertEqual(self.test_Cop1.outputs.count(), 1)
        self.assertEqual(self.test_Cop2.outputs.count(), 1)
        self.assertEqual(self.test_Dip1.inputs.count(), len_rc)
        self.assertEqual(self.test_Dip2.inputs.count(), len_rc)
        self.assertEqual(self.test_Dop.outputs.count(), len_rc)
        self.assertEqual(self.test_Eip1.inputs.count(), len_rc)
        self.assertEqual(self.test_Eip2.inputs.count(), len_rc)
        self.assertEqual(self.test_Eop.outputs.count(), len_rc)

        def same_resources(queryA, queryB):
            return set(queryA.values_list('resource__uuid', flat=True)) == set(queryB.values_list('resource__uuid', flat=True))
        self.assertTrue(same_resources(self.test_Aop.outputs, self.test_Cip1.inputs))
        self.assertTrue(same_resources(self.test_Bop.outputs, self.test_Cip2.inputs))
        self.assertTrue(same_resources(self.test_Cop1.outputs, self.test_Dip2.inputs))
        self.assertTrue(same_resources(self.test_Dop.outputs, self.test_Eip1.inputs))


        def assert_same_resource_types(op):
            op_types = op.output_port_type.resource_types.all().values_list('mimetype', flat=True)
            for o in op.outputs.all():
                r_type = o.resource.resource_type.mimetype
                self.assertIn(r_type, op_types)
        assert_same_resource_types(self.test_Aop)
        assert_same_resource_types(self.test_Bop)
        assert_same_resource_types(self.test_Cop1)
        assert_same_resource_types(self.test_Cop2)
        assert_same_resource_types(self.test_Dop)
        assert_same_resource_types(self.test_Eop)


        self.assertEqual(
            set(self.test_Aip.inputs.values_list('resource__uuid', flat=True)),
            set([self.test_resource.uuid])
        )
        self.assertEqual(
            set(self.test_Eip2.inputs.values_list('resource__uuid', flat=True)),
            set([self.test_resource.uuid])
        )
        self.assertEqual(
            set(self.test_Dip1.inputs.values_list('resource__uuid', flat=True)),
            set(map(lambda res: res.uuid, self.test_resourcecollection))
        )

        # names for resource collection
        rc_names_set = set(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
        Do_names_set = set([])
        for output in self.test_Dop.outputs.all():
            Do_names_set.add(output.resource.name)
        self.assertEqual(rc_names_set, Do_names_set)

        Eo_names_set = set([])
        for output in self.test_Eop.outputs.all():
            Eo_names_set.add(output.resource.name)
        self.assertEqual(rc_names_set, Eo_names_set)

        # automatic and manual
        rjA = self.test_wfjob_A.run_jobs.first()
        rjB = self.test_wfjob_B.run_jobs.first()
        rjC = self.test_wfjob_C.run_jobs.first()
        rjDs = self.test_wfjob_D.run_jobs.all()
        rjEs = self.test_wfjob_E.run_jobs.all()

        self.assertFalse(rjA.needs_input)
        self.assertFalse(rjA.ready_for_input)
        self.assertTrue(rjB.needs_input)
        self.assertTrue(rjB.ready_for_input)
        self.assertFalse(rjC.needs_input)
        self.assertFalse(rjC.ready_for_input)
        for rjDi in rjDs:
            self.assertTrue(rjDi.needs_input)
            self.assertFalse(rjDi.ready_for_input)
        for rjEi in rjEs:
            self.assertFalse(rjEi.needs_input)
            self.assertFalse(rjEi.ready_for_input)


    def test_execution(self):
        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/{0}/'.format(self.test_user.pk),
            'workflow': 'http://localhost:8000/workflow/{0}/'.format(self.test_workflow.uuid),
        }
        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        rjA = self.test_wfjob_A.run_jobs.first()
        rjB = self.test_wfjob_B.run_jobs.first()
        rjC = self.test_wfjob_C.run_jobs.first()
        rjDs = self.test_wfjob_D.run_jobs.all()
        rjEs = self.test_wfjob_E.run_jobs.all()

        Aout = self.test_Aop.outputs.first()
        Bout = self.test_Bop.outputs.first()
        Cout1 = self.test_Cop1.outputs.first()
        Cout2 = self.test_Cop2.outputs.first()
        Douts = self.test_Dop.outputs.all()
        Eouts = self.test_Eop.outputs.all()

        Ain = self.test_Aip.inputs.first()
        Cin1 = self.test_Cip1.inputs.first()
        Cin2 = self.test_Cip2.inputs.first()
        Din1s = self.test_Dip1.inputs.all()
        Din2s = self.test_Dip2.inputs.all()
        Ein1s = self.test_Eip1.inputs.all()
        Ein2s = self.test_Eip2.inputs.all()


        self.assertEqual(rjA.status, RunJobStatus.HAS_FINISHED)
        self.assertEqual(rjB.status, RunJobStatus.NOT_RUNNING)
        self.assertEqual(rjB.ready_for_input, True)
        self.assertEqual(rjC.status, RunJobStatus.NOT_RUNNING)
        for rjDi in rjDs:
            self.assertEqual(rjDi.status, RunJobStatus.NOT_RUNNING)
        for rjEi in rjEs:
            self.assertEqual(rjEi.status, RunJobStatus.NOT_RUNNING)

        self.assertTrue(Aout.resource.compat_resource_file)
        self.assertFalse(Bout.resource.compat_resource_file)
        self.assertFalse(Cout1.resource.compat_resource_file)
        self.assertFalse(Cout2.resource.compat_resource_file)
        for Douti in Douts:
            self.assertFalse(Douti.resource.compat_resource_file)
        for Eouti in Eouts:
            self.assertFalse(Eouti.resource.compat_resource_file)


        # Work with RunJob B
        response = self.client.post("/interactive/poly_mask/", {'run_job_uuid': str(rjB.uuid)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ## refetch
        rjA = self.test_wfjob_A.run_jobs.first()
        rjB = self.test_wfjob_B.run_jobs.first()
        rjC = self.test_wfjob_C.run_jobs.first()
        rjDs = self.test_wfjob_D.run_jobs.all()
        rjEs = self.test_wfjob_E.run_jobs.all()

        Aout = self.test_Aop.outputs.first()
        Bout = self.test_Bop.outputs.first()
        Cout1 = self.test_Cop1.outputs.first()
        Cout2 = self.test_Cop2.outputs.first()
        Douts = self.test_Dop.outputs.all()
        Eouts = self.test_Eop.outputs.all()

        Ain = self.test_Aip.inputs.first()
        Cin1 = self.test_Cip1.inputs.first()
        Cin2 = self.test_Cip2.inputs.first()
        Din1s = self.test_Dip1.inputs.all()
        Din2s = self.test_Dip2.inputs.all()
        Ein1s = self.test_Eip1.inputs.all()
        Ein2s = self.test_Eip2.inputs.all()

        self.assertEqual(rjB.status, RunJobStatus.HAS_FINISHED)
        self.assertEqual(rjB.needs_input, False)
        self.assertEqual(rjB.ready_for_input, False)
        self.assertEqual(rjC.status, RunJobStatus.HAS_FINISHED)
        for rjDi in rjDs:
            self.assertEqual(rjDi.status, RunJobStatus.NOT_RUNNING)
        for rjEi in rjEs:
            self.assertEqual(rjEi.status, RunJobStatus.NOT_RUNNING)

        self.assertTrue(Bout.resource.compat_resource_file)
        self.assertTrue(Cout1.resource.compat_resource_file)
        self.assertTrue(Cout2.resource.compat_resource_file)
        for Douti in Douts:
            self.assertFalse(Douti.resource.compat_resource_file)
        for Eouti in Eouts:
            self.assertFalse(Eouti.resource.compat_resource_file)

        # Work with one of RunJob D
        response = self.client.post("/interactive/poly_mask/", {'run_job_uuid': str(rjDs[0].uuid)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


        ## refetch
        rjA = self.test_wfjob_A.run_jobs.first()
        rjB = self.test_wfjob_B.run_jobs.first()
        rjC = self.test_wfjob_C.run_jobs.first()
        rjDs = self.test_wfjob_D.run_jobs.all()
        rjEs = self.test_wfjob_E.run_jobs.all()

        Aout = self.test_Aop.outputs.first()
        Bout = self.test_Bop.outputs.first()
        Cout1 = self.test_Cop1.outputs.first()
        Cout2 = self.test_Cop2.outputs.first()
        Douts = self.test_Dop.outputs.all()
        Eouts = self.test_Eop.outputs.all()

        Ain = self.test_Aip.inputs.first()
        Cin1 = self.test_Cip1.inputs.first()
        Cin2 = self.test_Cip2.inputs.first()
        Din1s = self.test_Dip1.inputs.all()
        Din2s = self.test_Dip2.inputs.all()
        Ein1s = self.test_Eip1.inputs.all()
        Ein2s = self.test_Eip2.inputs.all()

        rjD0 = rjDs[0]
        rjDremain = rjDs[1:]

        Dout0 = rjD0.outputs.get(output_port__output_port_type__name='out_typeA')
        rjE0 = Dout0.resource.inputs.all()[0].run_job
        Eout0 = rjE0.outputs.get(output_port__output_port_type__name='out_typeA')
        self.assertEqual(rjD0.status, RunJobStatus.HAS_FINISHED)
        self.assertEqual(rjD0.needs_input, False)
        self.assertEqual(rjD0.ready_for_input, False)
        self.assertTrue(Dout0.resource.compat_resource_file)
        self.assertEqual(rjE0.status, RunJobStatus.HAS_FINISHED)
        self.assertTrue(Eout0.resource.compat_resource_file)

        for rjDi in rjDremain:
            Douti = rjDi.outputs.get(output_port__output_port_type__name='out_typeA')
            rjEi = Douti.resource.inputs.all()[0].run_job
            Eouti = rjEi.outputs.get(output_port__output_port_type__name='out_typeA')
            self.assertEqual(rjDi.status, RunJobStatus.NOT_RUNNING)
            self.assertEqual(rjDi.needs_input, True)
            self.assertEqual(rjDi.ready_for_input, True)
            self.assertFalse(Douti.resource.compat_resource_file)
            self.assertEqual(rjEi.status, RunJobStatus.NOT_RUNNING)
            self.assertFalse(Eouti.resource.compat_resource_file)

        # Work with all Runjob Ds
        ## refetch
        rjA = self.test_wfjob_A.run_jobs.first()
        rjB = self.test_wfjob_B.run_jobs.first()
        rjC = self.test_wfjob_C.run_jobs.first()
        rjDs = self.test_wfjob_D.run_jobs.all()
        rjEs = self.test_wfjob_E.run_jobs.all()

        Aout = self.test_Aop.outputs.first()
        Bout = self.test_Bop.outputs.first()
        Cout1 = self.test_Cop1.outputs.first()
        Cout2 = self.test_Cop2.outputs.first()
        Douts = self.test_Dop.outputs.all()
        Eouts = self.test_Eop.outputs.all()

        Ain = self.test_Aip.inputs.first()
        Cin1 = self.test_Cip1.inputs.first()
        Cin2 = self.test_Cip2.inputs.first()
        Din1s = self.test_Dip1.inputs.all()
        Din2s = self.test_Dip2.inputs.all()
        Ein1s = self.test_Eip1.inputs.all()
        Ein2s = self.test_Eip2.inputs.all()

        for rjDi in rjDremain:
            response = self.client.post("/interactive/poly_mask/", {'run_job_uuid': str(rjDi.uuid)})
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        for rjDi in rjDs:
            self.assertEqual(rjDi.status, RunJobStatus.HAS_FINISHED)
            self.assertEqual(rjDi.needs_input, False)
            self.assertEqual(rjDi.ready_for_input, False)
        for Douti in Douts:
            self.assertTrue(Douti.resource.compat_resource_file)
        for rjEi in rjEs:
            self.assertEqual(rjEi.status, RunJobStatus.HAS_FINISHED)
        for Eouti in Eouts:
            self.assertTrue(Douti.resource.compat_resource_file)
