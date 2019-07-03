import shutil, os, uuid, time
from model_mommy import mommy
from django.contrib.auth.models import User
from rodan.models import Job, ResourceType
from django.core.files.base import ContentFile
from django.conf import settings


class RodanTestSetUpMixin(object):
    def url(self, obj):
        model_name = obj.__class__.__name__.lower()
        return "http://testserver/{0}/{1}/".format(model_name, obj.pk)

    def setUp_rodan(self):
        # ResourceTypes
        ResourceType.objects.create(
            mimetype="test/a1", description="", extension="ext_a1"
        )
        ResourceType.objects.create(
            mimetype="test/a2", description="", extension="ext_a2"
        )
        ResourceType.objects.create(
            mimetype="test/b", description="", extension="ext_b"
        )
        # Jobs
        import rodan.jobs.load  # just test if they are defined correctly and make no errors. Jobs are initialized by Celery thread.
        import rodan.test.dummy_jobs

        reload(rodan.test.dummy_jobs)

    def setUp_user(self):
        self.test_user = User.objects.create_user(
            username="ahankins", password="hahaha"
        )
        self.test_superuser = User.objects.create_superuser(
            username="super", email="s@s.com", password="hahaha"
        )

    def setUp_basic_workflow(self):
        """
        Workflow Graph:
        test_workflowjob => test_workflowjob2
        """

        self.test_job = mommy.make("rodan.Job")
        self.test_inputporttype = mommy.make(
            "rodan.InputPortType",
            maximum=3,
            minimum=1,
            is_list=False,
            job=self.test_job,
        )
        self.test_inputporttype.resource_types.add(
            ResourceType.objects.get(mimetype="test/a1"),
            ResourceType.objects.get(mimetype="test/a2"),
        )
        self.test_outputporttype = mommy.make(
            "rodan.OutputPortType",
            maximum=3,
            minimum=1,
            is_list=False,
            job=self.test_job,
        )
        self.test_outputporttype.resource_types.add(
            ResourceType.objects.get(mimetype="test/a1"),
            ResourceType.objects.get(mimetype="test/a2"),
        )

        self.test_project = mommy.make("rodan.Project")
        self.test_workflow = mommy.make("rodan.Workflow", project=self.test_project)

        # build this graph: test_workflowjob --> test_workflowjob2
        self.test_workflowjob = mommy.make(
            "rodan.WorkflowJob",
            workflow=self.test_workflow,
            job=self.test_job,
            job_settings={"a": 1, "b": [0.4]},
        )
        inputport = mommy.make(
            "rodan.InputPort",
            workflow_job=self.test_workflowjob,
            input_port_type=self.test_inputporttype,
        )
        outputport = mommy.make(
            "rodan.OutputPort",
            workflow_job=self.test_workflowjob,
            output_port_type=self.test_outputporttype,
        )

        test_connection = mommy.make(
            "rodan.Connection",
            output_port=outputport,
            input_port__input_port_type=self.test_inputporttype,
            input_port__workflow_job__workflow=self.test_workflow,
            input_port__workflow_job__job=self.test_job,
            input_port__workflow_job__job_settings={"a": 1, "b": [0.4]},
        )
        self.test_workflowjob2 = test_connection.input_port.workflow_job
        outputport2 = mommy.make(
            "rodan.OutputPort",
            workflow_job=self.test_workflowjob2,
            output_port_type=self.test_outputporttype,
        )

    def setUp_simple_dummy_workflow(self):
        """
        Workflow Graph:
        dummy_a_wfjob => dummy_m_wfjob
        """
        from rodan.test.dummy_jobs import dummy_automatic_job, dummy_manual_job

        dummy_a_job = Job.objects.get(name=dummy_automatic_job.name)
        dummy_m_job = Job.objects.get(name=dummy_manual_job.name)

        self.test_project = mommy.make("rodan.Project")
        self.test_workflow = mommy.make("rodan.Workflow", project=self.test_project)

        # build this graph: dummy_a_wfjob => dummy_m_wfjob
        self.dummy_a_wfjob = mommy.make(
            "rodan.WorkflowJob",
            workflow=self.test_workflow,
            job=dummy_a_job,
            job_settings={"a": 1, "b": [0.4]},
        )
        inputport_a = mommy.make(
            "rodan.InputPort",
            workflow_job=self.dummy_a_wfjob,
            input_port_type=dummy_a_job.input_port_types.filter(is_list=False).first(),
        )
        self.test_inputport_a = inputport_a
        outputport_a = mommy.make(
            "rodan.OutputPort",
            workflow_job=self.dummy_a_wfjob,
            output_port_type=dummy_a_job.output_port_types.filter(
                is_list=False
            ).first(),
        )

        self.dummy_m_wfjob = mommy.make(
            "rodan.WorkflowJob",
            workflow=self.test_workflow,
            job=dummy_m_job,
            job_settings={"a": 1, "b": [0.4]},
        )
        inputport_m = mommy.make(
            "rodan.InputPort",
            workflow_job=self.dummy_m_wfjob,
            input_port_type=dummy_m_job.input_port_types.filter(is_list=False).first(),
        )
        outputport_m = mommy.make(
            "rodan.OutputPort",
            workflow_job=self.dummy_m_wfjob,
            output_port_type=dummy_m_job.output_port_types.filter(
                is_list=False
            ).first(),
        )

        test_connection = mommy.make(
            "rodan.Connection", output_port=outputport_a, input_port=inputport_m
        )

    def setUp_resources_for_simple_dummy_workflow(self):
        self.test_resource = mommy.make(
            "rodan.Resource",
            project=self.test_project,
            resource_type=ResourceType.objects.get(mimetype="test/a1"),
        )
        self.test_resource.resource_file.save("dummy.txt", ContentFile("dummy text"))

        return {self.url(self.test_inputport_a): [self.url(self.test_resource)]}

    def setUp_complex_dummy_workflow(self):
        """
        Description of this complex dummy workflow: https://github.com/DDMAL/Rodan/wiki/New-Workflow-Model---WorkflowRun-Execution
        """
        from rodan.test.dummy_jobs import dummy_automatic_job, dummy_manual_job

        job_a = Job.objects.get(name=dummy_automatic_job.name)
        job_m = Job.objects.get(name=dummy_manual_job.name)

        ipt_aA = job_a.input_port_types.get(name="in_typeA")
        ipt_aB = job_a.input_port_types.get(name="in_typeB")
        ipt_aL = job_a.input_port_types.get(name="in_typeL")
        opt_aA = job_a.output_port_types.get(name="out_typeA")
        opt_aB = job_a.output_port_types.get(name="out_typeB")
        opt_aL = job_a.output_port_types.get(name="out_typeL")

        ipt_mA = job_m.input_port_types.get(name="in_typeA")
        ipt_mB = job_m.input_port_types.get(name="in_typeB")
        ipt_mL = job_m.input_port_types.get(name="in_typeL")
        opt_mA = job_m.output_port_types.get(name="out_typeA")
        opt_mB = job_m.output_port_types.get(name="out_typeB")
        opt_mL = job_m.output_port_types.get(name="out_typeL")

        self.test_project = mommy.make("rodan.Project")
        self.test_workflow = mommy.make("rodan.Workflow", project=self.test_project)

        self.test_wfjob_A = mommy.make(
            "rodan.WorkflowJob",
            workflow=self.test_workflow,
            job=job_a,
            job_settings={"a": 1, "b": [0.4]},
        )
        self.test_wfjob_B = mommy.make(
            "rodan.WorkflowJob",
            workflow=self.test_workflow,
            job=job_m,
            job_settings={"a": 1, "b": [0.4]},
        )
        self.test_wfjob_C = mommy.make(
            "rodan.WorkflowJob",
            workflow=self.test_workflow,
            job=job_a,
            job_settings={"a": 1, "b": [0.4]},
        )
        self.test_wfjob_D = mommy.make(
            "rodan.WorkflowJob",
            workflow=self.test_workflow,
            job=job_m,
            job_settings={"a": 1, "b": [0.4]},
        )
        self.test_wfjob_E = mommy.make(
            "rodan.WorkflowJob",
            workflow=self.test_workflow,
            job=job_a,
            job_settings={"a": 1, "b": [0.4]},
        )
        self.test_wfjob_F = mommy.make(
            "rodan.WorkflowJob",
            workflow=self.test_workflow,
            job=job_a,
            job_settings={"a": 1, "b": [0.4]},
        )

        self.test_Aip = mommy.make(
            "rodan.InputPort", workflow_job=self.test_wfjob_A, input_port_type=ipt_aA
        )
        self.test_Aop = mommy.make(
            "rodan.OutputPort", workflow_job=self.test_wfjob_A, output_port_type=opt_aA
        )
        self.test_Bop = mommy.make(
            "rodan.OutputPort", workflow_job=self.test_wfjob_B, output_port_type=opt_mL
        )

        self.test_Cip1 = mommy.make(
            "rodan.InputPort", workflow_job=self.test_wfjob_C, input_port_type=ipt_aB
        )
        self.test_Cip2 = mommy.make(
            "rodan.InputPort", workflow_job=self.test_wfjob_C, input_port_type=ipt_aL
        )
        self.test_Cop1 = mommy.make(
            "rodan.OutputPort", workflow_job=self.test_wfjob_C, output_port_type=opt_aA
        )
        self.test_Cop2 = mommy.make(
            "rodan.OutputPort", workflow_job=self.test_wfjob_C, output_port_type=opt_aB
        )

        self.test_Dip1 = mommy.make(
            "rodan.InputPort", workflow_job=self.test_wfjob_D, input_port_type=ipt_mA
        )
        self.test_Dip2 = mommy.make(
            "rodan.InputPort", workflow_job=self.test_wfjob_D, input_port_type=ipt_mB
        )
        self.test_Dip3 = mommy.make(
            "rodan.InputPort", workflow_job=self.test_wfjob_D, input_port_type=ipt_mL
        )
        self.test_Dop = mommy.make(
            "rodan.OutputPort", workflow_job=self.test_wfjob_D, output_port_type=opt_mA
        )

        self.test_Eip1 = mommy.make(
            "rodan.InputPort", workflow_job=self.test_wfjob_E, input_port_type=ipt_aA
        )
        self.test_Eip2 = mommy.make(
            "rodan.InputPort", workflow_job=self.test_wfjob_E, input_port_type=ipt_aB
        )
        self.test_Eop = mommy.make(
            "rodan.OutputPort", workflow_job=self.test_wfjob_E, output_port_type=opt_aA
        )

        self.test_Fip1 = mommy.make(
            "rodan.InputPort", workflow_job=self.test_wfjob_F, input_port_type=ipt_aA
        )
        self.test_Fip2 = mommy.make(
            "rodan.InputPort", workflow_job=self.test_wfjob_F, input_port_type=ipt_aA
        )
        self.test_Fop = mommy.make(
            "rodan.OutputPort", workflow_job=self.test_wfjob_F, output_port_type=opt_aL
        )

        self.test_conn_Aop_Cip1 = mommy.make(
            "rodan.Connection", output_port=self.test_Aop, input_port=self.test_Cip1
        )
        self.test_conn_Bop_Cip2 = mommy.make(
            "rodan.Connection", output_port=self.test_Bop, input_port=self.test_Cip2
        )
        self.test_conn_Cop1_Dip2 = mommy.make(
            "rodan.Connection", output_port=self.test_Cop1, input_port=self.test_Dip2
        )
        self.test_conn_Dop_Eip1 = mommy.make(
            "rodan.Connection", output_port=self.test_Dop, input_port=self.test_Eip1
        )
        self.test_conn_Dop_Fip2 = mommy.make(
            "rodan.Connection", output_port=self.test_Dop, input_port=self.test_Fip2
        )

    def setUp_resources_for_complex_dummy_workflow(self):
        self.test_resourcecollection = mommy.make(
            "rodan.Resource",
            _quantity=5,
            project=self.test_project,
            resource_type=ResourceType.objects.get(mimetype="test/a1"),
        ) + mommy.make(
            "rodan.Resource",
            _quantity=5,
            project=self.test_project,
            resource_type=ResourceType.objects.get(mimetype="test/a2"),
        )
        for index, res in enumerate(self.test_resourcecollection):
            res.name = str(index)  # 0 to 9
            res.save()
            res.resource_file.save("dummy.txt", ContentFile("dummy text"))

        self.test_resource = mommy.make(
            "rodan.Resource",
            project=self.test_project,
            resource_type=ResourceType.objects.get(mimetype="test/a1"),
        )

        self.test_resource.resource_file.save("dummy.txt", ContentFile("dummy text"))

        self.test_resourcelist = mommy.make(
            "rodan.ResourceList", project=self.test_project
        )
        self.test_resources_in_resource_list = mommy.make(
            "rodan.Resource",
            _quantity=8,
            project=self.test_project,
            resource_type=ResourceType.objects.get(mimetype="test/a1"),
        )
        for index, res in enumerate(self.test_resources_in_resource_list):
            res.name = str(index)  # 0 to 9
            res.save()
            res.resource_file.save("dummy.txt", ContentFile("dummy text"))
        self.test_resourcelist.resources.add(*self.test_resources_in_resource_list)

        # print("self.test_Dip1", self.url(self.test_Dip1))
        # print("self.test_Fip1", self.url(self.test_Fip1))
        # print("self.test_Aip", self.url(self.test_Aip))
        # print("self.test_Eip2", self.url(self.test_Eip2))
        # print("self.test_Dip3", self.url(self.test_Dip3))
        return {
            self.url(self.test_Dip1): map(self.url, self.test_resourcecollection),
            self.url(self.test_Fip1): map(self.url, self.test_resourcecollection),
            self.url(self.test_Aip): [self.url(self.test_resource)],
            self.url(self.test_Eip2): [self.url(self.test_resource)],
            self.url(self.test_Dip3): [self.url(self.test_resourcelist)],
        }


class RodanTestTearDownMixin(object):
    """
    Please put this mixin on the leftmost place in the parent classes
    to let tearDown() method take effect, like:

        class ProjectViewTestCase(RodanTestTearDownMixin, APITestCase)
    """

    def tearDown(self):
        # clean up the temporary filesystem
        if os.path.isdir(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)
