from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rodan.models import (
    WorkflowJob,
    WorkflowJobGroup,
    InputPort,
    OutputPort,
    Connection,
    Workflow,
    Job,
)
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
from model_mommy import mommy


class WorkflowJobGroupViewTestCase(
    RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin
):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.test_workflow1 = mommy.make("rodan.Workflow")
        self.test_workflow2 = mommy.make("rodan.Workflow")
        self.test_workflowjob1 = mommy.make(
            "rodan.WorkflowJob", workflow=self.test_workflow1
        )
        self.test_workflowjob1b = mommy.make(
            "rodan.WorkflowJob", workflow=self.test_workflow1
        )
        self.test_workflowjob2 = mommy.make(
            "rodan.WorkflowJob", workflow=self.test_workflow2
        )
        self.client.force_authenticate(user=self.test_superuser)

    def test_create_and_autoset_workflow(self):
        wfjgroup_obj = {
            "workflow_jobs": [
                reverse("workflowjob-detail", kwargs={"pk": self.test_workflowjob1.uuid}),
                reverse("workflowjob-detail", kwargs={"pk": self.test_workflowjob1b.uuid}),
            ],
            "name": "test group",
        }
        response = self.client.post("/api/workflowjobgroups/", wfjgroup_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wfjgroup_uuid = response.data["uuid"]
        wfjg = WorkflowJobGroup.objects.get(uuid=wfjgroup_uuid)
        self.assertEqual(wfjg.workflow, self.test_workflow1)

        wfjgroup_obj = {
            "workflow_jobs": [
                "http://localhost:8000/api/workflowjob/{0}/".format(
                    self.test_workflowjob2.uuid
                )
            ]
        }
        response = self.client.patch(
            "/api/workflowjobgroup/{0}/".format(wfjgroup_uuid), wfjgroup_obj, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        wfjg = WorkflowJobGroup.objects.get(uuid=wfjgroup_uuid)  # refetch
        self.assertEqual(wfjg.workflow, self.test_workflow2)

    def test_create_conflict_wfjgroup(self):
        wfjgroup_obj = {
            "workflow_jobs": [
                "http://localhost:8000/api/workflowjob/{0}/".format(
                    self.test_workflowjob1.uuid
                ),
                "http://localhost:8000/api/workflowjob/{0}/".format(
                    self.test_workflowjob2.uuid
                ),
            ],
            "name": "test group",
        }
        response = self.client.post("/api/workflowjobgroups/", wfjgroup_obj, format="json")
        anticipated_message = {
            "workflow_jobs": ["All WorkflowJobs should belong to the same Workflow."]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_patch_conflict_wfjgroup(self):
        wfjgroup_obj = {
            "workflow_jobs": [
                "http://localhost:8000/api/workflowjob/{0}/".format(
                    self.test_workflowjob1.uuid
                )
            ],
            "name": "test group",
        }
        response = self.client.post("/api/workflowjobgroups/", wfjgroup_obj, format="json")
        assert response.status_code == status.HTTP_201_CREATED, "This should pass"
        wfjgroup_uuid = response.data["uuid"]

        wfjgroup_obj = {
            "workflow_jobs": [
                "http://localhost:8000/api/workflowjob/{0}/".format(
                    self.test_workflowjob1.uuid
                ),
                "http://localhost:8000/api/workflowjob/{0}/".format(
                    self.test_workflowjob2.uuid
                ),
            ]
        }
        response = self.client.patch(
            "/api/workflowjobgroup/{0}/".format(wfjgroup_uuid), wfjgroup_obj, format="json"
        )
        anticipated_message = {
            "workflow_jobs": ["All WorkflowJobs should belong to the same Workflow."]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_create_empty_workflowjobgroup(self):
        wfjgroup_obj = {"workflow_jobs": [], "name": "empty group"}
        response = self.client.post("/api/workflowjobgroups/", wfjgroup_obj, format="json")
        anticipated_message = {
            "workflow_jobs": ["Empty WorkflowJobGroup is not allowed."]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_patch_empty_workflowjobgroup(self):
        wfjgroup_obj = {
            "workflow_jobs": [
                "http://localhost:8000/api/workflowjob/{0}/".format(
                    self.test_workflowjob1.uuid
                )
            ],
            "name": "test group",
        }
        response = self.client.post("/api/workflowjobgroups/", wfjgroup_obj, format="json")
        assert response.status_code == status.HTTP_201_CREATED, "This should pass"
        wfjgroup_uuid = response.data["uuid"]

        wfjgroup_obj = {"workflow_jobs": []}
        response = self.client.patch(
            "/api/workflowjobgroup/{0}/".format(wfjgroup_uuid), wfjgroup_obj, format="json"
        )
        anticipated_message = {
            "workflow_jobs": ["Empty WorkflowJobGroup is not allowed."]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)


class WorkflowJobGroupActionTestCase(
    RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin
):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_complex_dummy_workflow()
        self.client.force_authenticate(user=self.test_superuser)

    def test_import_valid_workflow(self):
        self.test_workflow.valid = True
        self.test_workflow.save()
        self.test_new_workflow = mommy.make("rodan.Workflow")
        mommy.make(
            "rodan.WorkflowJob", workflow=self.test_new_workflow
        )  # make it non-null
        wfjgroup_obj = {
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_new_workflow.pk
            ),
            "origin": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.pk
            ),
        }
        response = self.client.post("/api/workflowjobgroups/", wfjgroup_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # wfjgroup_uuid = response.data["uuid"]

        # Check object numbers
        self.assertEqual(
            WorkflowJob.objects.filter(workflow=self.test_new_workflow).count(), 6 + 1
        )
        self.assertEqual(
            InputPort.objects.filter(
                workflow_job__workflow=self.test_new_workflow
            ).count(),
            10,
        )
        self.assertEqual(
            OutputPort.objects.filter(
                workflow_job__workflow=self.test_new_workflow
            ).count(),
            7,
        )
        self.assertEqual(
            Connection.objects.filter(
                input_port__workflow_job__workflow=self.test_new_workflow
            ).count(),
            5,
        )

    def test_import_invalid_workflow(self):
        self.test_workflow.valid = False
        self.test_workflow.save()
        self.test_new_workflow = mommy.make("rodan.Workflow")
        mommy.make(
            "rodan.WorkflowJob", workflow=self.test_new_workflow
        )  # make it non-null
        wfjgroup_obj = {
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_new_workflow.pk
            ),
            "origin": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.pk
            ),
        }
        response = self.client.post("/api/workflowjobgroups/", wfjgroup_obj, format="json")
        anticipated_message = {"origin": ["Origin workflow must be valid."]}

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_export_workflowjobgroup(self):
        wfjgroup_obj = {
            "workflow_jobs": [
                "http://localhost:8000/api/workflowjob/{0}/".format(self.test_wfjob_A.uuid),
                "http://localhost:8000/api/workflowjob/{0}/".format(self.test_wfjob_B.uuid),
                "http://localhost:8000/api/workflowjob/{0}/".format(self.test_wfjob_C.uuid),
            ],
            "name": "hahaha",
        }
        response = self.client.post("/api/workflowjobgroups/", wfjgroup_obj, format="json")
        assert response.status_code == status.HTTP_201_CREATED, "This should pass"
        wfjgroup_uuid = response.data["uuid"]

        project = mommy.make("rodan.Project")
        wf_obj = {
            "workflow_job_group": "http://localhost:8000/api/workflowjobgroup/{0}/".format(
                wfjgroup_uuid
            ),
            "project": "http://localhost:8000/api/project/{0}/".format(project.pk),
        }
        response = self.client.post("/api/workflows/", wf_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wf_uuid = response.data["uuid"]
        wf = Workflow.objects.get(uuid=wf_uuid)

        # Check object numbers
        self.assertEqual(WorkflowJob.objects.filter(workflow=wf).count(), 3)
        self.assertEqual(InputPort.objects.filter(workflow_job__workflow=wf).count(), 3)
        self.assertEqual(
            OutputPort.objects.filter(workflow_job__workflow=wf).count(), 4
        )
        self.assertEqual(
            Connection.objects.filter(input_port__workflow_job__workflow=wf).count(), 2
        )


class WorkflowJobGroupProtectTestCase(
    RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin
):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_complex_dummy_workflow()
        self.client.force_authenticate(user=self.test_superuser)
        wfjgroup1_obj = {
            "workflow_jobs": [
                "http://localhost:8000/api/workflowjob/{0}/".format(self.test_wfjob_B.uuid),
                "http://localhost:8000/api/workflowjob/{0}/".format(self.test_wfjob_C.uuid),
            ],
            "name": "hahaha",
        }
        response = self.client.post("/api/workflowjobgroups/", wfjgroup1_obj, format="json")
        assert response.status_code == status.HTTP_201_CREATED, "This should pass"

        wfjgroup2_obj = {
            "workflow_jobs": [
                "http://localhost:8000/api/workflowjob/{0}/".format(self.test_wfjob_D.uuid),
                "http://localhost:8000/api/workflowjob/{0}/".format(self.test_wfjob_E.uuid),
            ],
            "name": "hahaha",
        }
        response = self.client.post("/api/workflowjobgroups/", wfjgroup2_obj, format="json")
        assert response.status_code == status.HTTP_201_CREATED, "This should pass"

    def test_cannot_delete_workflowjob_in_group(self):
        anticipated_message = {
            "detail": "To delete this workflowjob, you should first remove it from the group."
        }
        for wfjob in [
            self.test_wfjob_B,
            self.test_wfjob_C,
            self.test_wfjob_D,
            self.test_wfjob_E,
        ]:
            response = self.client.delete("/api/workflowjob/{0}/".format(wfjob.pk))
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data, anticipated_message)
        for wfjob in [self.test_wfjob_A, self.test_wfjob_F]:
            response = self.client.delete(
                "/api/workflowjob/{0}/?format=json".format(wfjob.pk)
            )
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_can_change_workflowjob_job_settings_in_group(self):
        settings_update = {"job_settings": {"a": 1}}

        for wfjob in [
            self.test_wfjob_B,
            self.test_wfjob_C,
            self.test_wfjob_D,
            self.test_wfjob_E,
        ]:
            response = self.client.patch(
                "/api/workflowjob/{0}/".format(wfjob.pk), settings_update, format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["job_settings"], {"a": 1})

    def test_cannot_change_workflowjob_job__name__workflow_in_group(self):
        from rodan.test.dummy_jobs import dummy_automatic_job

        # from rodan.test.dummy_jobs import dummy_manual_job

        job_a = Job.objects.get(name=dummy_automatic_job.name)
        # job_m = Job.objects.get(name=dummy_manual_job.name)
        wfj_updates = {
            "job": "http://localhost:8000/api/job/{0}/".format(job_a.pk),
            "name": "new name",
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                mommy.make("rodan.Workflow").pk
            ),
        }
        for k, v in wfj_updates.items():
            anticipated_message = {
                k: "To modify this field, you should first remove it from the group."
            }
            wfj_update = {k: v}
            for wfjob in [
                self.test_wfjob_B,
                self.test_wfjob_C,
                self.test_wfjob_D,
                self.test_wfjob_E,
            ]:
                response = self.client.patch(
                    "/api/workflowjob/{0}/".format(wfjob.pk), wfj_update, format="json"
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, anticipated_message)
            for wfjob in [self.test_wfjob_A, self.test_wfjob_F]:
                response = self.client.patch(
                    "/api/workflowjob/{0}/".format(wfjob.pk), wfj_update, format="json"
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_delete_inputport_in_group(self):
        anticipated_message = {
            "detail": (
                "To delete this input port, you should first remove its "
                "workflow job from the group."
            )
        }
        for ip in [
            self.test_Cip1,
            self.test_Cip2,
            self.test_Dip1,
            self.test_Dip2,
            self.test_Dip3,
            self.test_Eip1,
            self.test_Eip2,
        ]:
            response = self.client.delete("/api/inputport/{0}/".format(ip.pk))
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data, anticipated_message)
        for ip in [self.test_Aip, self.test_Fip1, self.test_Fip2]:
            response = self.client.delete("/api/inputport/{0}/?format=json".format(ip.pk))
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_cannot_modify_inputport_in_group(self):
        from rodan.test.dummy_jobs import dummy_automatic_job

        # from rodan.test.dummy_jobs import dummy_manual_job

        job_a = Job.objects.get(name=dummy_automatic_job.name)
        # job_m = Job.objects.get(name=dummy_manual_job.name)
        ipt_aA = job_a.input_port_types.get(name="in_typeA")
        ip_updates = {
            "input_port_type": "http://localhost:8000/api/inputporttype/{0}/".format(
                ipt_aA.pk
            ),
            "label": "aaa",
            "workflow_job": "http://localhost:8000/api/workflowjob/{0}/".format(
                self.test_wfjob_A.pk
            ),
        }

        for k, v in ip_updates.items():
            anticipated_message = {
                k: "To modify this field, you should first remove its workflow job from the group."
            }
            ip_update = {k: v}
            for ip in [
                self.test_Cip1,
                self.test_Cip2,
                self.test_Dip1,
                self.test_Dip2,
                self.test_Dip3,
                self.test_Eip1,
                self.test_Eip2,
            ]:
                response = self.client.patch(
                    "/api/inputport/{0}/".format(ip.pk), ip_update, format="json"
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, anticipated_message)
            for ip in [self.test_Aip, self.test_Fip1, self.test_Fip2]:
                response = self.client.patch(
                    "/api/inputport/{0}/".format(ip.pk), ip_update, format="json"
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_delete_outputport_in_group(self):
        anticipated_message = {
            "detail": (
                "To delete this output port, you should first remove its "
                "workflow job from the group."
            )
        }
        for op in [
            self.test_Bop,
            self.test_Cop1,
            self.test_Cop2,
            self.test_Dop,
            self.test_Eop,
        ]:
            response = self.client.delete("/api/outputport/{0}/".format(op.pk))
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data, anticipated_message)
        for op in [self.test_Aop, self.test_Fop]:
            response = self.client.delete("/api/outputport/{0}/?format=json".format(op.pk))
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_cannot_modify_outputport_in_group(self):
        from rodan.test.dummy_jobs import dummy_automatic_job

        # from rodan.test.dummy_jobs import dummy_manual_job

        job_a = Job.objects.get(name=dummy_automatic_job.name)
        # job_m = Job.objects.get(name=dummy_manual_job.name)
        opt_aA = job_a.output_port_types.get(name="out_typeA")
        op_updates = {
            "output_port_type": "http://localhost:8000/api/outputporttype/{0}/".format(
                opt_aA.pk
            ),
            "label": "aaa",
            "workflow_job": "http://localhost:8000/api/workflowjob/{0}/".format(
                self.test_wfjob_A.pk
            ),
        }

        for k, v in op_updates.items():
            anticipated_message = {
                k: "To modify this field, you should first remove its workflow job from the group."
            }
            op_update = {k: v}
            for op in [
                self.test_Bop,
                self.test_Cop1,
                self.test_Cop2,
                self.test_Dop,
                self.test_Eop,
            ]:
                response = self.client.patch(
                    # "/api/outputport/{0}/".format(op.pk), op_update, format="json"
                    reverse("outputport-detail", kwargs={"pk": op.pk}), op_update, format="json"
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, anticipated_message)
            for op in [self.test_Aop, self.test_Fop]:
                response = self.client.patch(
                    "/api/outputport/{0}/".format(op.pk), op_update, format="json"
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_delete_connection_in_group(self):
        anticipated_message = {
            "detail": (
                "To delete this connection, you should first remove one of its"
                " related workflow jobs from the group."
            )
        }
        for conn in [self.test_conn_Bop_Cip2, self.test_conn_Dop_Eip1]:
            response = self.client.delete("/api/connection/{0}/".format(conn.pk))
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data, anticipated_message)
        for conn in [
            self.test_conn_Aop_Cip1,
            self.test_conn_Cop1_Dip2,
            self.test_conn_Dop_Fip2,
        ]:
            response = self.client.delete(
                "/api/connection/{0}/?format=json".format(conn.pk)
            )
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_cannot_modify_connection_in_group(self):
        conn_updates = {
            "output_port": "http://localhost:8000/api/outputport/{0}/".format(
                self.test_Aop.pk
            ),
            "input_port": "http://localhost:8000/api/inputport/{0}/".format(
                self.test_Fip2.pk
            ),
        }

        for k, v in conn_updates.items():
            anticipated_message = {
                k: (
                    "To modify this field, you should first remove one of its"
                    " related workflow jobs from the group."
                )
            }
            conn_update = {k: v}
            for conn in [self.test_conn_Bop_Cip2, self.test_conn_Dop_Eip1]:
                response = self.client.patch(
                    "/api/connection/{0}/".format(conn.pk), conn_update, format="json"
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.data, anticipated_message)
            for conn in [
                self.test_conn_Aop_Cip1,
                self.test_conn_Cop1_Dip2,
                self.test_conn_Dop_Fip2,
            ]:
                response = self.client.patch(
                    "/api/connection/{0}/".format(conn.pk), conn_update, format="json"
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)
