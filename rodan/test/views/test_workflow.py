from django.conf import settings
from django.contrib.auth.models import User
from rodan.models import Project, WorkflowJob, Workflow, InputPort, InputPortType, OutputPort, OutputPortType, Resource, Connection, Job, ResourceType

from rest_framework.test import APITestCase
from rest_framework import status

from model_mommy import mommy
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
import uuid
from rodan.serializers.workflow import version_map

class WorkflowViewTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    """
        For clarification of some of the more confusing tests (i.e. loop, merging, and branching), see
        https://github.com/DDMAL/Rodan/wiki/Workflow-View-Test
    """

    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_basic_workflow()
        self.client.force_authenticate(user=self.test_superuser)

    def _validate(self, workflow_uuid):
        workflow_update = {
            'valid': True,
        }
        return self.client.patch("/workflow/{0}/".format(workflow_uuid), workflow_update, format='json')


    def test_view__workflow_notfound(self):
        response = self._validate(uuid.uuid1())
        anticipated_message = {'detail': 'Not found.'}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    def test_view__posting_valid(self):
        workflow_obj = {
            'project': 'http://localhost:8000/project/{0}/'.format(self.test_project.uuid),
            'name': "test workflow",
            'valid': True,
        }
        response = self.client.post("/workflows/", workflow_obj, format='json')
        anticipated_message = {'valid': ["You can't create a valid workflow - it must be validated through a PATCH request."]}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_view__post(self):
        workflow_obj = {
            'project': 'http://localhost:8000/project/{0}/'.format(self.test_project.uuid),
            'name': "test workflow",
            'creator': 'http://localhost:8000/user/{0}/'.format(self.test_superuser.pk),
            'valid': False,
        }
        response = self.client.post("/workflows/", workflow_obj, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    def test_view__validation_result_valid(self):
        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        retr_workflow = Workflow.objects.get(pk=self.test_workflow.uuid)
        self.assertTrue(retr_workflow.valid)
    def test_view__validation_result_invalid(self):
        test_workflow_no_jobs = mommy.make('rodan.Workflow', project=self.test_project)
        response = self._validate(test_workflow_no_jobs.uuid)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        retr_workflow = Workflow.objects.get(pk=test_workflow_no_jobs.uuid)
        self.assertFalse(retr_workflow.valid)

    def test_workflowjob__no_output(self):
        self.test_workflowjob2.output_ports.all().delete()
        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error_code'], 'WFJ_NO_OP')
    def test_workflowjob__inputport_number_not_satisfy(self):
        mommy.make('rodan.Connection', _quantity=10,
                   output_port=self.test_workflowjob.output_ports.all()[0],
                   input_port__workflow_job=self.test_workflowjob2,
                   input_port__input_port_type=self.test_inputporttype)
        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error_code'], 'WFJ_TOO_MANY_IP')
    def test_workflowjob__outputport_number_not_satisfy(self):
        mommy.make('rodan.Connection', _quantity=10,
                   output_port__workflow_job=self.test_workflowjob,
                   output_port__output_port_type=self.test_outputporttype,
                   input_port__workflow_job__job=self.test_workflowjob2.job)
        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error_code'], 'WFJ_TOO_MANY_OP')
    def test_workflowjob__settings_not_satisfy(self):
        self.test_job.settings = {
            'type': 'object',
            'required': ['a'],
            'properties': {'a': {'type': 'number'}}
        }
        self.test_job.save()
        self.test_workflowjob.job_settings = {'b': []}
        self.test_workflowjob.save()
        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error_code'], 'WFJ_INVALID_SETTINGS')


    def test_input__type_incompatible_with_job(self):
        new_ipt = mommy.make('rodan.InputPortType')
        new_ip = mommy.make('rodan.InputPort',
                            workflow_job=self.test_workflowjob,
                            input_port_type=new_ipt)

        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error_code'], 'IP_TYPE_MISMATCH')
    def test_input__multiple_connections(self):
        ip = self.test_workflowjob2.input_ports.all()[0]
        mommy.make('rodan.Connection',
                   output_port=self.test_workflowjob.output_ports.all()[0],
                   input_port=ip)
        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error_code'], 'IP_TOO_MANY_CONNECTIONS')

    def test_input__more_than_maximum(self):
        for i in range(self.test_inputporttype.maximum):
            ip = mommy.make('rodan.InputPort',
                            workflow_job=self.test_workflowjob,
                            input_port_type=self.test_inputporttype)
        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error_code'], 'WFJ_TOO_MANY_IP')
    def test_input__fewer_than_minimum(self):
        ip = self.test_workflowjob.input_ports.all()[0]
        ip.delete()
        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error_code'], 'WFJ_TOO_FEW_IP')


    def test_output__type_incompatible_with_job(self):
        new_opt = mommy.make('rodan.OutputPortType')
        new_op = mommy.make('rodan.OutputPort',
                            workflow_job=self.test_workflowjob,
                            output_port_type=new_opt)

        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error_code'], 'OP_TYPE_MISMATCH')
    def test_output__more_than_maximum(self):
        for o in range(self.test_outputporttype.maximum):
            op = mommy.make('rodan.OutputPort',
                            workflow_job=self.test_workflowjob,
                            output_port_type=self.test_outputporttype)
        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error_code'], 'WFJ_TOO_MANY_OP')
    def test_output__fewer_than_minimum(self):
        opt2 = mommy.make('rodan.OutputPortType',
                          maximum=3,
                          minimum=1,
                          job=self.test_job)
        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error_code'], 'WFJ_TOO_FEW_OP')
    def test_output__resourcetype_list_conflict_case1(self):
        # CASE 1: input_port is list but output_type not.
        new_ipt = mommy.make('rodan.InputPortType',
                             maximum=1,
                             minimum=0,
                             job=self.test_job,
                             is_list=True)
        new_ipt.resource_types.add(ResourceType.objects.get(mimetype='test/b'))
        new_ip = mommy.make('rodan.InputPort',
                            workflow_job=self.test_workflowjob2,
                            input_port_type=new_ipt)
        op = self.test_workflowjob.output_ports.first()
        conn = mommy.make('rodan.Connection',
                          output_port=op,
                          input_port=new_ip)
        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error_code'], 'RESOURCETYPE_LIST_CONFLICT')

    def test_output__resourcetype_list_conflict_case2(self):
        # CASE 2: output_port is list but input_type not.
        new_opt = mommy.make('rodan.OutputPortType',
                             maximum=1,
                             minimum=0,
                             job=self.test_job,
                             is_list=True)
        new_opt.resource_types.add(ResourceType.objects.get(mimetype='test/b'))
        new_op = mommy.make('rodan.OutputPort',
                            workflow_job=self.test_workflowjob,
                            output_port_type=new_opt)

        ipt = self.test_workflowjob.input_ports.first().input_port_type
        new_ip = mommy.make('rodan.InputPort',
                            workflow_job=self.test_workflowjob,
                            input_port_type=ipt)

        conn = mommy.make('rodan.Connection',
                          output_port=new_op,
                          input_port=new_ip)
        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error_code'], 'RESOURCETYPE_LIST_CONFLICT')

    def test_output__no_common_resource_type_simple(self):
        new_ipt = mommy.make('rodan.InputPortType',
                             maximum=1,
                             minimum=0,
                             is_list=False,
                             job=self.test_job)
        new_ipt.resource_types.add(ResourceType.objects.get(mimetype='test/b')) # consider the type of opt is 'test/a1' and 'test/a2'
        new_ip = mommy.make('rodan.InputPort',
                            workflow_job=self.test_workflowjob2,
                            input_port_type=new_ipt)
        op = self.test_workflowjob.output_ports.first()
        conn = mommy.make('rodan.Connection',
                          output_port=op,
                          input_port=new_ip)
        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error_code'], 'NO_COMMON_RESOURCETYPE')
    def test_output__no_common_resource_type_complex(self):
        new_ipt1 = mommy.make('rodan.InputPortType',
                              maximum=1,
                              minimum=0,
                              is_list=False,
                              job=self.test_job)
        new_ipt1.resource_types.add(ResourceType.objects.get(mimetype='test/a1')) # consider the type of opt is 'test/a1' and 'test/a2'
        new_ipt2 = mommy.make('rodan.InputPortType',
                              maximum=1,
                              minimum=0,
                              is_list=False,
                              job=self.test_job)
        new_ipt2.resource_types.add(ResourceType.objects.get(mimetype='test/a2')) # consider the type of opt is 'test/a1' and 'test/a2'
        new_ip1 = mommy.make('rodan.InputPort',
                             workflow_job=self.test_workflowjob2,
                             input_port_type=new_ipt1)
        new_ip2 = mommy.make('rodan.InputPort',
                             workflow_job=self.test_workflowjob2,
                             input_port_type=new_ipt2)
        op = self.test_workflowjob.output_ports.first()
        conn1 = mommy.make('rodan.Connection',
                           output_port=op,
                           input_port=new_ip1)
        conn2 = mommy.make('rodan.Connection',
                           output_port=op,
                           input_port=new_ip2)
        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error_code'], 'NO_COMMON_RESOURCETYPE')

    def test_graph__empty(self):
        test_workflow_no_jobs = mommy.make('rodan.Workflow', project=self.test_project)
        response = self._validate(test_workflow_no_jobs.uuid)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error_code'], 'WF_EMPTY')
    def test_graph__not_connected(self):
        workflowjob = mommy.make('rodan.WorkflowJob',
                                 workflow=self.test_workflow,
                                 job=self.test_job)
        inputport = mommy.make('rodan.InputPort',
                               workflow_job=workflowjob,
                               input_port_type=self.test_inputporttype)
        outputport = mommy.make('rodan.OutputPort',
                                workflow_job=workflowjob,
                                output_port_type=self.test_outputporttype)

        test_connection = mommy.make('rodan.Connection',
                                     output_port=outputport,
                                     input_port__input_port_type=self.test_inputporttype,
                                     input_port__workflow_job__workflow=self.test_workflow,
                                     input_port__workflow_job__job=self.test_job)
        test_workflowjob2 = test_connection.input_port.workflow_job
        outputport2 = mommy.make('rodan.OutputPort',
                                 workflow_job=test_workflowjob2,
                                 output_port_type=self.test_outputporttype)

        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error_code'], 'WF_NOT_CONNECTED')
    def test_graph__loop(self):
        mommy.make('rodan.Connection',
                   input_port__input_port_type=self.test_inputporttype,
                   input_port__workflow_job=self.test_workflowjob,
                   output_port__output_port_type=self.test_outputporttype,
                   output_port__workflow_job=self.test_workflowjob2)

        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error_code'], 'WF_HAS_CYCLES')
    def test_graph__merging_workflow(self):
        test_no_input_workflowjob = mommy.make('rodan.WorkflowJob',
                                               workflow=self.test_workflow)
        opt_for_no_input = mommy.make('rodan.OutputPortType',
                                      minimum=0,
                                      maximum=10,
                                      is_list=False,
                                      job=test_no_input_workflowjob.job)
        opt_for_no_input.resource_types.add(ResourceType.objects.get(mimetype='test/a1'))
        mommy.make('rodan.Connection',
                   output_port__workflow_job=test_no_input_workflowjob,
                   output_port__output_port_type=opt_for_no_input,
                   input_port__workflow_job=self.test_workflowjob2,
                   input_port__input_port_type=self.test_inputporttype)

        test_connection3 = mommy.make('rodan.Connection',
                                      output_port=self.test_workflowjob2.output_ports.all()[0],
                                      input_port__input_port_type=self.test_inputporttype,
                                      input_port__workflow_job__workflow=self.test_workflow,
                                      input_port__workflow_job__job=self.test_job)
        self.test_workflowjob3 = test_connection3.input_port.workflow_job
        mommy.make('rodan.OutputPort',
                   workflow_job=self.test_workflowjob3,
                   output_port_type=self.test_outputporttype)
        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_graph__branching_workflow(self):
        test_connection3 = mommy.make('rodan.Connection',
                                      output_port__output_port_type=self.test_outputporttype,
                                      output_port__workflow_job=self.test_workflowjob2,
                                      input_port__input_port_type=self.test_inputporttype,
                                      input_port__workflow_job__workflow=self.test_workflow,
                                      input_port__workflow_job__job=self.test_job)
        self.test_workflowjob3 = test_connection3.input_port.workflow_job
        mommy.make('rodan.OutputPort',
                   workflow_job=self.test_workflowjob3,
                   output_port_type=self.test_outputporttype)

        test_connection2 = mommy.make('rodan.Connection',
                                      output_port__output_port_type=self.test_outputporttype,
                                      output_port__workflow_job=self.test_workflowjob2,
                                      input_port__input_port_type=self.test_inputporttype,
                                      input_port__workflow_job__workflow=self.test_workflow,
                                      input_port__workflow_job__job=self.test_job)
        self.test_second_output_workflowjob = test_connection2.input_port.workflow_job
        mommy.make('rodan.OutputPort',
                   workflow_job=self.test_second_output_workflowjob,
                   output_port_type=self.test_outputporttype)

        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_graph__branching_and_merging(self):
        """
        wfjob------>wfjob_2------------>wfjob_5
             `----->wfjob_3----wfjob_4--^
        """
        self.test_workflowjob3 = mommy.make('rodan.WorkflowJob',
                                            workflow=self.test_workflow,
                                            job=self.test_job)
        self.test_workflowjob4 = mommy.make('rodan.WorkflowJob',
                                            workflow=self.test_workflow,
                                            job=self.test_job)
        self.test_workflowjob5 = mommy.make('rodan.WorkflowJob',
                                            workflow=self.test_workflow,
                                            job=self.test_job)
        outputport1 = self.test_workflowjob.output_ports.first()
        outputport2 = self.test_workflowjob2.output_ports.first()
        inputport3 = mommy.make('rodan.InputPort',
                                workflow_job=self.test_workflowjob3,
                                input_port_type=self.test_inputporttype)
        outputport3 = mommy.make('rodan.OutputPort',
                                 workflow_job=self.test_workflowjob3,
                                 output_port_type=self.test_outputporttype)
        inputport4 = mommy.make('rodan.InputPort',
                                workflow_job=self.test_workflowjob4,
                                input_port_type=self.test_inputporttype)
        outputport4 = mommy.make('rodan.OutputPort',
                                 workflow_job=self.test_workflowjob4,
                                 output_port_type=self.test_outputporttype)
        inputport5A = mommy.make('rodan.InputPort',
                                workflow_job=self.test_workflowjob5,
                                input_port_type=self.test_inputporttype)
        inputport5B = mommy.make('rodan.InputPort',
                                workflow_job=self.test_workflowjob5,
                                input_port_type=self.test_inputporttype)
        outputport5 = mommy.make('rodan.OutputPort',
                                 workflow_job=self.test_workflowjob5,
                                 output_port_type=self.test_outputporttype)
        mommy.make('rodan.Connection',
                   output_port=outputport1,
                   input_port=inputport3)
        mommy.make('rodan.Connection',
                   output_port=outputport3,
                   input_port=inputport4)
        mommy.make('rodan.Connection',
                   output_port=outputport4,
                   input_port=inputport5A)

        mommy.make('rodan.Connection',
                   output_port=outputport2,
                   input_port=inputport5B)

        response = self._validate(self.test_workflow.uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class WorkflowSerializationTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    """
        For clarification of some of the more confusing tests (i.e. loop, merging, and branching), see
        https://github.com/DDMAL/Rodan/wiki/Workflow-View-Test
    """

    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_simple_dummy_workflow()
        self.client.force_authenticate(user=self.test_superuser)

    def test_export(self):
        response = self.client.get("/workflow/{0}/?export=yes".format(self.test_workflow.uuid))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = version_map[settings.RODAN_WORKFLOW_SERIALIZATION_FORMAT_VERSION]
        try:
            serializer.validate(response.data)
        except serializer.ValidationError as e:
            self.fail('Exported workflow does not validate: {0}'.format(e.detail))
    def test_import_0_1(self):
        serializer = version_map[0.1]
        serialized = serializer.dump(self.test_workflow)
        response = self.client.post("/workflows/", {
            'serialized': serialized,
            'project': "http://localhost:8000/project/{0}/".format(self.test_project.uuid)
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.test_project.workflows.count(), 2)

        serialized['workflow_jobs'][0]['job_name'] = 'hahahaha'
        response = self.client.post("/workflows/", {
            'serialized': serialized,
            'project': "http://localhost:8000/project/{0}/".format(self.test_project.uuid)
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'serialized': {'workflow_jobs[0].job_name': u'Job hahahaha does not exist in current Rodan installation.'}})


class WorkflowExternPortsTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.client.force_authenticate(user=self.test_superuser)

    def _validate(self, workflow_uuid):
        workflow_update = {
            'valid': True,
        }
        return self.client.patch("/workflow/{0}/".format(workflow_uuid), workflow_update, format='json')

    def test_simple_workflow(self):
        self.setUp_simple_dummy_workflow()
        response = self._validate(self.test_workflow.uuid)
        assert response.status_code == status.HTTP_200_OK

        ip_a = self.dummy_a_wfjob.input_ports.first()
        op_a = self.dummy_a_wfjob.output_ports.first()
        ip_m = self.dummy_m_wfjob.input_ports.first()
        op_m = self.dummy_m_wfjob.output_ports.first()

        self.assertTrue(ip_a.extern)
        self.assertFalse(op_a.extern)
        self.assertFalse(ip_m.extern)
        self.assertTrue(op_m.extern)

    def test_simple_workflow_update_all(self):
        self.setUp_simple_dummy_workflow()
        ip_a = self.dummy_a_wfjob.input_ports.first()
        op_a = self.dummy_a_wfjob.output_ports.first()
        ip_m = self.dummy_m_wfjob.input_ports.first()
        op_m = self.dummy_m_wfjob.output_ports.first()

        ip_a.extern = False
        ip_a.save()
        op_a.extern = True
        op_a.save()
        ip_m.extern = True
        ip_m.save()
        op_m.extern = False
        op_m.save()

        response = self._validate(self.test_workflow.uuid)
        assert response.status_code == status.HTTP_200_OK

        ip_a = self.dummy_a_wfjob.input_ports.first()
        op_a = self.dummy_a_wfjob.output_ports.first()
        ip_m = self.dummy_m_wfjob.input_ports.first()
        op_m = self.dummy_m_wfjob.output_ports.first()

        self.assertTrue(ip_a.extern)
        self.assertFalse(op_a.extern)
        self.assertFalse(ip_m.extern)
        self.assertTrue(op_m.extern)

    def test_complex_workflow(self):
        self.setUp_complex_dummy_workflow()
        response = self._validate(self.test_workflow.uuid)
        assert response.status_code == status.HTTP_200_OK

        # refetch and test
        Aip = InputPort.objects.get(uuid=self.test_Aip.uuid)
        self.assertTrue(Aip.extern)
        Aop = OutputPort.objects.get(uuid=self.test_Aop.uuid)
        self.assertFalse(Aop.extern)

        Bop = OutputPort.objects.get(uuid=self.test_Bop.uuid)
        self.assertFalse(Bop.extern)

        Cip1 = InputPort.objects.get(uuid=self.test_Cip1.uuid)
        self.assertFalse(Cip1.extern)
        Cip2 = InputPort.objects.get(uuid=self.test_Cip2.uuid)
        self.assertFalse(Cip2.extern)
        Cop1 = OutputPort.objects.get(uuid=self.test_Cop1.uuid)
        self.assertFalse(Cop1.extern)
        Cop2 = OutputPort.objects.get(uuid=self.test_Cop2.uuid)
        self.assertTrue(Cop2.extern)

        Dip1 = InputPort.objects.get(uuid=self.test_Dip1.uuid)
        self.assertTrue(Dip1.extern)
        Dip2 = InputPort.objects.get(uuid=self.test_Dip2.uuid)
        self.assertFalse(Dip2.extern)
        Dop = OutputPort.objects.get(uuid=self.test_Dop.uuid)
        self.assertFalse(Dop.extern)

        Eip1 = InputPort.objects.get(uuid=self.test_Eip1.uuid)
        self.assertFalse(Eip1.extern)
        Eip2 = InputPort.objects.get(uuid=self.test_Eip2.uuid)
        self.assertTrue(Eip2.extern)
        Eop = OutputPort.objects.get(uuid=self.test_Eop.uuid)
        self.assertTrue(Eop.extern)

        Fip1 = InputPort.objects.get(uuid=self.test_Fip1.uuid)
        self.assertTrue(Fip1.extern)
        Fip2 = InputPort.objects.get(uuid=self.test_Fip2.uuid)
        self.assertFalse(Fip2.extern)
        Fop = OutputPort.objects.get(uuid=self.test_Fop.uuid)
        self.assertTrue(Fop.extern)
