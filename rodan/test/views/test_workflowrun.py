import os
import json
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse

from rodan.models import WorkflowRun, ResourceType
from model_mommy import mommy
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
import uuid
from django.core.files.base import ContentFile
from rodan.constants import task_status


class WorkflowRunViewTest(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_simple_dummy_workflow()
        self.client.force_authenticate(user=self.test_superuser)
        response = self.client.patch(
            reverse("workflow-detail", kwargs={"pk": self.test_workflow.uuid}),
            {"valid": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list(self):
        # response = self.client.get("/api/workflowruns/")
        response = self.client.get(reverse("workflowrun-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_no_workflow_ID(self):
        workflowrun_obj = {}

        # response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        response = self.client.post(
            reverse("workflowrun-list"), workflowrun_obj, format="json")
        anticipated_message = {"workflow": ["This field is required."]}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_no_existing_workflow(self):
        workflowrun_obj = {
            # "workflow": "http://localhost:8000/api/workflow/{0}/".format(uuid.uuid1())
            "workflow": reverse("workflow-detail", kwargs={"pk": uuid.uuid1()})
        }

        # response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        anticipated_message = {
            "workflow": ["Invalid hyperlink - Object does not exist."]
        }
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_status(self):
        # anticipated_message = {'status': ['Can only create a WorkflowRun that has
        # SCHEDULED status.']}
        anticipated_message = {
            "status": ["Can only create a WorkflowRun that requests processing."]
        }
        workflowrun_obj = {
            # "workflow": "http://localhost:8000/api/workflow/{0}/".format(
            #     self.test_workflow.uuid
            # ),
            "workflow": reverse("workflow-detail", kwargs={"pk": self.test_workflow.uuid}),
            "status": task_status.CANCELLED,
        }

        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        workflowrun_obj["status"] = task_status.FINISHED
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        workflowrun_obj["status"] = task_status.FAILED
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        workflowrun_obj["status"] = task_status.PROCESSING
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        workflowrun_obj["status"] = task_status.REQUEST_CANCELLING
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        workflowrun_obj["status"] = task_status.REQUEST_RETRYING
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_invalid_workflow(self):
        self.test_workflow.valid = False
        self.test_workflow.save()
        workflowrun_obj = {
            # "workflow": "http://localhost:8000/api/workflow/{0}/".format(
            #     self.test_workflow.uuid
            # ),
            "workflow": reverse("workflow-detail", kwargs={"pk": self.test_workflow.uuid}),
            "status": task_status.REQUEST_PROCESSING
        }

        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        anticipated_message = {
            "workflow": ["Workflow must be valid before you can run it."]
        }
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_not_found(self):
        workflowrun_update = {"status": task_status.CANCELLED}
        response = self.client.patch(
            # "/workflowrun/{0}/".format(uuid.uuid1()), workflowrun_update, format="json"
            reverse("workflowrun-detail", kwargs={"pk": uuid.uuid1()}),
            workflowrun_update,
            format="json"
        )
        anticipated_message = {"detail": "Not found."}
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(anticipated_message, response.data)


class WorkflowRunResourceAssignmentTest(
    RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin
):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_complex_dummy_workflow()
        self.client.force_authenticate(user=self.test_superuser)
        response = self.client.patch(
            reverse("workflow-detail", kwargs={"pk": self.test_workflow.uuid}),
            {"valid": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_valid_assignment(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        workflowrun_obj = {
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.uuid
            ),
            "resource_assignments": ra,
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_valid_assignment__with_list_of_resource_lists(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        ra[self.url(self.test_Dip1)] = [self.url(self.test_resource)]
        ra[self.url(self.test_Fip1)] = [self.url(self.test_resource)]

        resource_lists = []
        for i in range(10):
            rl = mommy.make(
                "rodan.ResourceList",
                project=self.test_project,
                resource_type=ResourceType.objects.get(mimetype="test/a2"),
            )
            rs = mommy.make(
                "rodan.Resource",
                _quantity=5,
                project=self.test_project,
                resource_type=ResourceType.objects.get(mimetype="test/a2"),
            )
            for index, res in enumerate(rs):
                res.name = str(index)  # 0 to 9
                res.save()
                res.resource_file.save("dummy.txt", ContentFile("dummy text"))
            rl.resources.add(*rs)
            resource_lists.append(rl)
        ra[self.url(self.test_Dip3)] = map(self.url, resource_lists)

        workflowrun_obj = {
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.uuid
            ),
            "resource_assignments": ra,
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_no_resource_assignments(self):
        workflowrun_obj = {
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.uuid
            )
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        anticipated_message = {"resource_assignments": ["This field is required"]}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_json_object(self):
        workflowrun_obj = {
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.uuid
            ),
            "resource_assignments": [],  # not a JSON object
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        anticipated_message = {
            "resource_assignments": ["This field must be a JSON object"]
        }
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_satisfied_input_port(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        ra[self.url(self.test_Eip1)] = [self.url(self.test_resource)]
        workflowrun_obj = {
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.uuid
            ),
            "resource_assignments": ra,
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        anticipated_message = {
            "resource_assignments": {
                self.url(self.test_Eip1): ["Assigned InputPort must be unsatisfied"]
            }
        }
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_input_port(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        ra["invalid url"] = [self.url(self.test_resource)]
        workflowrun_obj = {
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.uuid
            ),
            "resource_assignments": ra,
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        anticipated_message = {
            "resource_assignments": {
                "invalid url": [u"Invalid hyperlink - No URL match."]
            }
        }
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_still_unsatisfied_input_port(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        del ra[self.url(self.test_Aip)]
        workflowrun_obj = {
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.uuid
            ),
            "resource_assignments": ra,
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        anticipated_message = {
            "resource_assignments": [
                "There are still unsatisfied InputPorts: {0}".format(
                    self.url(self.test_Aip)
                )
            ]
        }
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resources_not_a_list(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        ra[self.url(self.test_Aip)] = self.url(self.test_resource)
        workflowrun_obj = {
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.uuid
            ),
            "resource_assignments": ra,
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        anticipated_message = {
            "resource_assignments": {
                self.url(self.test_Aip): [
                    "A list of resources or resource lists is expected"
                ]
            }
        }
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resources_empty(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        ra[self.url(self.test_Aip)] = []
        workflowrun_obj = {
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.uuid
            ),
            "resource_assignments": ra,
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        anticipated_message = {
            "resource_assignments": {
                self.url(self.test_Aip): [
                    "It is not allowed to assign an empty collection"
                ]
            }
        }
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_multiple_resource_collections_same_length(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        another_resource_collection = mommy.make(
            "rodan.Resource",
            _quantity=10,
            name="dummy",
            project=self.test_project,
            resource_type=ResourceType.objects.get(mimetype="test/a1"),
        )
        for index, res in enumerate(another_resource_collection):
            # Making the resources ready
            res.resource_file.save("dummy.txt", ContentFile("dummy text"))

        ra[self.url(self.test_Fip1)] = list(map(self.url, another_resource_collection))

        workflowrun_obj = {
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.uuid
            ),
            "resource_assignments": ra,
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_multiple_resource_collections_different_lengths(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        ra[self.url(self.test_Fip1)] = ra[self.url(self.test_Fip1)][:-1]
        workflowrun_obj = {
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.uuid
            ),
            "resource_assignments": ra,
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        anticipated_message1 = {
            "resource_assignments": {
                self.url(self.test_Fip1): [
                    (
                        "The number of assigned Resources of ResourceLists is not even"
                        " with that of {}"
                    ).format(self.url(self.test_Dip1))
                ]
            }
        }
        anticipated_message2 = {
            "resource_assignments": {
                self.url(self.test_Dip1): [
                    (
                        "The number of assigned Resources of ResourceLists is not even with "
                        "that of {}"
                    ).format(self.url(self.test_Fip1))
                ]
            }
        }
        self.assertIn(response.data, [anticipated_message1, anticipated_message2])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resource_not_in_project(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        res = self.test_resourcecollection[5]
        res.project = mommy.make("rodan.Project")
        res.save()
        workflowrun_obj = {
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.uuid
            ),
            "resource_assignments": ra,
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        anticipated_message1 = {
            "resource_assignments": {
                self.url(self.test_Fip1): {
                    5: ["Resource or ResourceList is not in the project of Workflow"]
                }
            }
        }
        anticipated_message2 = {
            "resource_assignments": {
                self.url(self.test_Dip1): {
                    5: ["Resource or ResourceList is not in the project of Workflow"]
                }
            }
        }
        self.assertIn(response.data, [anticipated_message1, anticipated_message2])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resource_type_not_match(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        res = self.test_resourcecollection[5]
        res.resource_type = ResourceType.objects.get(mimetype="test/b")
        res.save()
        workflowrun_obj = {
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.uuid
            ),
            "resource_assignments": ra,
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # The expected structure of error response is:
        # {'resource_assignments': {input_port_url: {5:
        #   ['The resource type <ResourceType test/b> does not match the InputPort
        #   {test/a1 or test/a2}']}}}

        self.assertEqual(len(response.data["resource_assignments"]), 1)
        error_ip, error_detail = next(
            iter(response.data["resource_assignments"].items())
        )
        self.assertIn(error_ip, [self.url(self.test_Fip1), self.url(self.test_Dip1)])

        self.assertEqual(len(error_detail), 1)
        error_position, error_list = next(iter(error_detail.items()))
        self.assertEqual(error_position, 5)

        self.assertEqual(len(error_list), 1)
        error_message = error_list[0]

        self.assertTrue(
            error_message.startswith(
                "The resource type <ResourceType test/b> does not match"
            )
        )
        self.assertIn("test/a1", error_message)
        self.assertIn("test/a2", error_message)

    def test_assign_resource_to_list_ports(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        pos = len(self.test_resourcecollection)
        ra[self.url(self.test_Dip1)].append(self.url(self.test_resourcelist))
        ra[self.url(self.test_Fip1)].append(self.url(self.test_resourcelist))
        workflowrun_obj = {
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.uuid
            ),
            "resource_assignments": ra,
        }
        response = self.client.post(
            # "/workflowruns/?format=json", workflowrun_obj, format="json"
            reverse("workflowrun-list"), workflowrun_obj, format="json"
        )

        # raise Exception(response)
        anticipated_message1 = {
            "resource_assignments": {
                self.url(self.test_Fip1): {
                    pos: [
                        "The InputPort requires Resources but is provided with ResourceLists"
                    ]
                }
            }
        }
        anticipated_message2 = {
            "resource_assignments": {
                self.url(self.test_Dip1): {
                    pos: [
                        "The InputPort requires Resources but is provided with ResourceLists"
                    ]
                }
            }
        }

        self.assertIn(response.data, [anticipated_message1, anticipated_message2])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_resource_list_to_nonlist_ports(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        ra[self.url(self.test_Dip3)] = map(self.url, self.test_resourcecollection)
        workflowrun_obj = {
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.uuid
            ),
            "resource_assignments": ra,
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        anticipated_message = {
            "resource_assignments": {
                self.url(self.test_Dip3): {
                    0: [
                        "The InputPort requires ResourceLists but is provided with Resources"
                    ]
                }
            }
        }
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resource_list_not_in_project(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        self.test_resourcelist.project = mommy.make("rodan.Project")
        self.test_resourcelist.save()
        workflowrun_obj = {
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.uuid
            ),
            "resource_assignments": ra,
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        anticipated_message = {
            "resource_assignments": {
                self.url(self.test_Dip3): {
                    0: ["Resource or ResourceList is not in the project of Workflow"]
                }
            }
        }
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resource_type_not_match__in_resource_list(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        for index, res in enumerate(self.test_resources_in_resource_list):
            res.resource_type = ResourceType.objects.get(mimetype="test/b")
            res.save()
        workflowrun_obj = {
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.uuid
            ),
            "resource_assignments": ra,
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # The expected structure of error response is:
        # {'resource_assignments': {self.url(self.test_Dip3):
        #   {0: ['The resource type <ResourceType test/b> does not match the InputPort
        #   {test/a1 or test/a2}']}}}

        self.assertEqual(len(response.data["resource_assignments"]), 1)
        error_ip, error_detail = next(
            iter(response.data["resource_assignments"].items())
        )
        self.assertEqual(error_ip, self.url(self.test_Dip3))

        self.assertEqual(len(error_detail), 1)
        error_position, error_list = next(iter(error_detail.items()))
        self.assertEqual(error_position, 0)

        self.assertEqual(len(error_list), 1)
        error_message = error_list[0]

        self.assertTrue(
            error_message.startswith(
                "The resource type <ResourceType test/b> does not match"
            )
        )
        self.assertIn("test/a1", error_message)
        self.assertIn("test/a2", error_message)


class WorkflowRunSimpleExecutionTest(
    RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin
):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_simple_dummy_workflow()
        self.client.force_authenticate(user=self.test_superuser)
        response = self.client.patch(
            reverse("workflow-detail", kwargs={"pk": self.test_workflow.uuid}),
            {"valid": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_successful_execution(self):
        ra = self.setUp_resources_for_simple_dummy_workflow()
        workflowrun_obj = {
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.uuid
            ),
            "resource_assignments": ra,
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wfrun_id = response.data["uuid"]
        wfrun = WorkflowRun.objects.get(uuid=wfrun_id)
        self.assertEqual(wfrun.creator.pk, self.test_superuser.pk)

        dummy_a_runjob = self.dummy_a_wfjob.run_jobs.first()
        dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()

        # self.assertEqual(dummy_a_runjob.status, task_status.SCHEDULED)
        # self.assertEqual(dummy_m_runjob.status, task_status.SCHEDULED)
        # self.assertEqual(WorkflowRun.objects.get(uuid=wfrun_id).status, task_status.SCHEDULED)

        # workflowrun_update = {'status': task_status.REQUEST_PROCESSING}
        # response = self.client.patch(
        #     "/workflowrun/{0}/".format(str(wfrun_id)), workflowrun_update, format='json')
        # self.assertEqual(response.status_code, status.HTTP_200_OK)

        # dummy_a_runjob = self.dummy_a_wfjob.run_jobs.first()
        # dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()

        # At this point, the automatic RunJob should be finished, and the manual
        # RunJob should wait for input
        self.assertEqual(dummy_a_runjob.status, task_status.FINISHED)
        self.assertEqual(dummy_m_runjob.status, task_status.WAITING_FOR_INPUT)
        self.assertEqual(
            WorkflowRun.objects.get(uuid=wfrun_id).status, task_status.PROCESSING
        )

        response = self.client.post(
            "/api/interactive/{0}/acquire/".format(str(dummy_m_runjob.uuid))
            # reverse("interactive-acquire", kwargs={"pk": str(dummy_m_runjob.uuid)})
        )
        assert response.status_code == status.HTTP_200_OK
        user_input = ["any", "thing"]
        response = self.client.post(
            response.data["working_url"], user_input, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # then manual job should be flagged as finished and should have result
        with open(dummy_m_runjob.outputs.first().resource.resource_file.path) as f:
            self.assertEqual(json.load(f), user_input)
        dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()  # refetch
        self.assertEqual(dummy_m_runjob.status, task_status.FINISHED)
        self.assertEqual(
            WorkflowRun.objects.get(uuid=wfrun_id).status, task_status.FINISHED
        )

    def test_automatic_job_fail(self):
        with self.settings(
            CELERY_EAGER_PROPAGATES_EXCEPTIONS=False
        ):  # Turn off propagation as task will fail
            ra = self.setUp_resources_for_simple_dummy_workflow()
            self.test_resource.resource_file.save("dummy.txt", ContentFile("will fail"))

            workflowrun_obj = {
                "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                    self.test_workflow.uuid
                ),
                "resource_assignments": ra,
            }

            response = self.client.post(
                # "/workflowruns/", workflowrun_obj, format="json"
                reverse("workflowrun-list"), workflowrun_obj, format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            wfrun_id = response.data["uuid"]

            # workflowrun_update = {'status': task_status.REQUEST_PROCESSING}
            # response = self.client.patch(
            #   "/workflowrun/{0}/".format(str(wfrun_id)), workflowrun_update, format='json')
            # self.assertEqual(response.status_code, status.HTTP_200_OK)

            dummy_a_runjob = self.dummy_a_wfjob.run_jobs.first()
            dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()

            # At this point, the automatic RunJob should fail, and the manual RunJob
            # should not accept input
            self.assertEqual(dummy_a_runjob.status, task_status.FAILED)
            self.assertEqual(dummy_a_runjob.error_summary, "dummy automatic job error")
            self.assertEqual(dummy_m_runjob.status, task_status.SCHEDULED)
            self.assertEqual(
                WorkflowRun.objects.get(uuid=wfrun_id).status, task_status.FAILED
            )

    def test_manual_job_rejected(self):
        ra = self.setUp_resources_for_simple_dummy_workflow()
        self.test_resource.resource_file.save("dummy.txt", ContentFile("dummy text"))

        workflowrun_obj = {
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.uuid
            ),
            "resource_assignments": ra,
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wfrun_id = response.data["uuid"]

        # workflowrun_update = {'status': task_status.REQUEST_PROCESSING}
        # response = self.client.patch(
        #   "/workflowrun/{0}/".format(str(wfrun_id)), workflowrun_update, format='json')
        # self.assertEqual(response.status_code, status.HTTP_200_OK)

        dummy_a_runjob = self.dummy_a_wfjob.run_jobs.first()
        dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()

        # At this point, the automatic RunJob should be finished, and the manual RunJob should
        # wait for input
        self.assertEqual(dummy_a_runjob.status, task_status.FINISHED)
        self.assertEqual(dummy_m_runjob.status, task_status.WAITING_FOR_INPUT)

        response = self.client.post(
            "/api/interactive/{0}/acquire/".format(str(dummy_m_runjob.uuid))
            # reverse("interactive-acquire", kwargs={"pk": str(dummy_m_runjob.uuid)})
        )
        assert response.status_code == status.HTTP_200_OK
        user_input = {"fail": "hahaha"}
        response = self.client.post(response.data["working_url"], user_input)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()  # refetch
        self.assertEqual(dummy_m_runjob.status, task_status.WAITING_FOR_INPUT)
        self.assertEqual(
            WorkflowRun.objects.get(uuid=wfrun_id).status, task_status.PROCESSING
        )

    def test_cancel_retry_redo(self):
        # [TODO] When there's time, try these tests again in the Travis Docker image.
        # For whatever reason, this and one another test always fail on travis only.
        # They do not fail locally. For some reason on travis, trying to revoke a
        # task gets a Connection Failed.
        if os.environ.get("TRAVIS", "False") != "true":
            ra = self.setUp_resources_for_simple_dummy_workflow()
            self.test_resource.resource_file.save("dummy.txt", ContentFile("dummy text"))

            workflowrun_obj = {
                "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                    self.test_workflow.uuid
                ),
                "resource_assignments": ra,
            }
            response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            wfrun_uuid = response.data["uuid"]

            response = self.client.patch(
                # "/workflowrun/{0}/".format(wfrun_uuid),
                reverse("workflowrun-detail", kwargs={"pk": wfrun_uuid}),
                {"status": task_status.REQUEST_CANCELLING},
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()
            self.assertEqual(dummy_m_runjob.status, task_status.CANCELLED)
            self.assertEqual(
                WorkflowRun.objects.get(uuid=wfrun_uuid).status, task_status.CANCELLED
            )

            workflowrun_update = {"status": task_status.PROCESSING}
            response = self.client.patch(
                # "/workflowrun/{0}/".format(wfrun_uuid), workflowrun_update, format="json"
                reverse("workflowrun-detail", kwargs={"pk": wfrun_uuid}),
                workflowrun_update,
                format="json"
            )
            anticipated_message = {"status": ["Invalid status update"]}
            self.assertEqual(anticipated_message, response.data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                WorkflowRun.objects.get(uuid=wfrun_uuid).status, task_status.CANCELLED
            )

            workflowrun_update = {"status": task_status.REQUEST_RETRYING}
            response = self.client.patch(
                # "/workflowrun/{0}/".format(wfrun_uuid), workflowrun_update, format="json"
                reverse("workflowrun-detail", kwargs={"pk": wfrun_uuid}),
                workflowrun_update,
                format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()
            self.assertEqual(dummy_m_runjob.status, task_status.WAITING_FOR_INPUT)
            self.assertEqual(
                WorkflowRun.objects.get(uuid=wfrun_uuid).status, task_status.RETRYING
            )

            workflowrun_update = {
                # "last_redone_runjob_tree": "http://localhost:8000/runjob/{0}/".format(
                #     dummy_m_runjob.uuid
                # )
                "last_redone_runjob_tree": reverse(
                    "runjob-detail", kwargs={"pk": dummy_m_runjob.uuid}
                )
            }
            response = self.client.patch(
                # "/workflowrun/{0}/".format(wfrun_uuid), workflowrun_update, format="json"
                reverse("workflowrun-detail", kwargs={"pk": wfrun_uuid}),
                workflowrun_update,
                format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            dummy_m_runjob = self.dummy_m_wfjob.run_jobs.first()
            self.assertEqual(dummy_m_runjob.status, task_status.WAITING_FOR_INPUT)
            self.assertEqual(
                WorkflowRun.objects.get(uuid=wfrun_uuid).status, task_status.RETRYING
            )

    def test_post_cancelled(self):
        ra = self.setUp_resources_for_simple_dummy_workflow()
        workflowrun_obj = {
            # "workflow": "http://localhost:8000/api/workflow/{0}/".format(
            #     self.test_workflow.uuid
            # ),
            "workflow": reverse(
                "workflowrun-detail", kwargs={"pk": self.test_workflow.uuid}
            ),
            "status": task_status.CANCELLED,
            "resource_assignments": ra,
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class WorkflowRunComplexTest(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    "Test workflowrun creation and execution with a complex workflow."

    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_complex_dummy_workflow()
        self.client.force_authenticate(user=self.test_superuser)
        response = self.client.patch(
            reverse("workflow-detail", kwargs={"pk": self.test_workflow.uuid}),
            {"valid": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_creation(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        workflowrun_obj = {
            "workflow": reverse("workflow-detail", kwargs={"pk": self.test_workflow.uuid}),
            "resource_assignments": ra,
        }
        # response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wfrun_id = response.data["uuid"]

        len_rc = len(self.test_resourcecollection)
        self.assertEqual(self.test_wfjob_A.run_jobs.count(), 1)
        self.assertEqual(self.test_wfjob_B.run_jobs.count(), 1)
        self.assertEqual(self.test_wfjob_C.run_jobs.count(), 1)
        self.assertEqual(self.test_wfjob_D.run_jobs.count(), len_rc)
        self.assertEqual(self.test_wfjob_E.run_jobs.count(), len_rc)
        self.assertEqual(self.test_wfjob_F.run_jobs.count(), len_rc)

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
        self.assertEqual(self.test_Fip1.inputs.count(), len_rc)
        self.assertEqual(self.test_Fip2.inputs.count(), len_rc)
        self.assertEqual(self.test_Fop.outputs.count(), len_rc)

        def same_resources(queryA, queryB):
            return set(queryA.values_list("resource__uuid", flat=True)) == set(
                queryB.values_list("resource__uuid", flat=True)
            )

        self.assertTrue(same_resources(self.test_Aop.outputs, self.test_Cip1.inputs))
        self.assertTrue(same_resources(self.test_Bop.outputs, self.test_Cip2.inputs))
        self.assertTrue(same_resources(self.test_Cop1.outputs, self.test_Dip2.inputs))
        self.assertTrue(same_resources(self.test_Dop.outputs, self.test_Eip1.inputs))
        self.assertTrue(same_resources(self.test_Dop.outputs, self.test_Fip2.inputs))

        def assert_same_resource_types(op):
            op_types = op.output_port_type.resource_types.all().values_list(
                "mimetype", flat=True
            )
            for o in op.outputs.all():
                if op.output_port_type.is_list:
                    r = o.resource_list
                    if r.resources.count() > 0:
                        r_type = r.resource_type.mimetype
                        self.assertIn(r_type, op_types)
                else:
                    r = o.resource
                    r_type = r.resource_type.mimetype
                    self.assertIn(r_type, op_types)

        assert_same_resource_types(self.test_Aop)
        assert_same_resource_types(self.test_Bop)
        assert_same_resource_types(self.test_Cop1)
        assert_same_resource_types(self.test_Cop2)
        assert_same_resource_types(self.test_Dop)
        assert_same_resource_types(self.test_Eop)
        assert_same_resource_types(self.test_Fop)

        self.assertEqual(
            set(self.test_Aip.inputs.values_list("resource__uuid", flat=True)),
            set([self.test_resource.uuid]),
        )
        self.assertEqual(
            set(self.test_Eip2.inputs.values_list("resource__uuid", flat=True)),
            set([self.test_resource.uuid]),
        )
        self.assertEqual(
            set(self.test_Dip3.inputs.values_list("resource_list__uuid", flat=True)),
            set([self.test_resourcelist.uuid]),
        )
        self.assertEqual(
            set(self.test_Dip1.inputs.values_list("resource__uuid", flat=True)),
            set(map(lambda res: res.uuid, self.test_resourcecollection)),
        )
        self.assertEqual(
            set(self.test_Fip1.inputs.values_list("resource__uuid", flat=True)),
            set(map(lambda res: res.uuid, self.test_resourcecollection)),
        )

        # names for resource collection
        rc_names_set = set(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
        Do_names_set = set([])
        for output in self.test_Dop.outputs.all():
            Do_names_set.add(output.resource.name)
        self.assertEqual(rc_names_set, Do_names_set)

        Eo_names_set = set([])
        for output in self.test_Eop.outputs.all():
            Eo_names_set.add(output.resource.name)
        self.assertEqual(rc_names_set, Eo_names_set)

        Fo_names_set = set([])
        for output in self.test_Fop.outputs.all():
            Fo_names_set.add(output.resource_list.name)
        self.assertEqual(rc_names_set, Fo_names_set)

        # self.assertEqual(WorkflowRun.objects.get(uuid=wfrun_id).status, task_status.SCHEDULED)
        self.assertEqual(
            WorkflowRun.objects.get(uuid=wfrun_id).status, task_status.PROCESSING
        )

    def test_execution(self):
        ra = self.setUp_resources_for_complex_dummy_workflow()
        workflowrun_obj = {
            # "workflow": "http://localhost:8000/api/workflow/{0}/".format(
            #     self.test_workflow.uuid
            # ),
            "workflow": reverse("workflow-detail", kwargs={"pk": self.test_workflow.uuid}),
            "resource_assignments": ra,
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wfrun_id = response.data["uuid"]

        # workflowrun_update = {'status': task_status.REQUEST_PROCESSING}
        # response = self.client.patch(
        #     "/workflowrun/{0}/".format(str(wfrun_id)), workflowrun_update, format='json')
        # self.assertEqual(response.status_code, status.HTTP_200_OK)

        rjA = self.test_wfjob_A.run_jobs.first()  # noqa
        rjB = self.test_wfjob_B.run_jobs.first()  # noqa
        rjC = self.test_wfjob_C.run_jobs.first()  # noqa
        rjDs = self.test_wfjob_D.run_jobs.all()  # noqa
        rjEs = self.test_wfjob_E.run_jobs.all()  # noqa
        rjFs = self.test_wfjob_F.run_jobs.all()  # noqa

        Aout = self.test_Aop.outputs.first()  # noqa
        Bout = self.test_Bop.outputs.first()  # noqa
        Cout1 = self.test_Cop1.outputs.first()  # noqa
        Cout2 = self.test_Cop2.outputs.first()  # noqa
        Douts = self.test_Dop.outputs.all()  # noqa
        Eouts = self.test_Eop.outputs.all()  # noqa
        Fouts = self.test_Fop.outputs.all()  # noqa

        Ain = self.test_Aip.inputs.first()  # noqa
        Cin1 = self.test_Cip1.inputs.first()  # noqa
        Cin2 = self.test_Cip2.inputs.first()  # noqa
        Din1s = self.test_Dip1.inputs.all()  # noqa
        Din2s = self.test_Dip2.inputs.all()  # noqa
        Din3s = self.test_Dip3.inputs.all()  # noqa
        Ein1s = self.test_Eip1.inputs.all()  # noqa
        Ein2s = self.test_Eip2.inputs.all()  # noqa
        Fins = self.test_Eip1.inputs.all()  # noqa

        self.assertEqual(rjA.status, task_status.FINISHED)
        self.assertEqual(rjB.status, task_status.WAITING_FOR_INPUT)
        self.assertEqual(rjC.status, task_status.SCHEDULED)
        for rjDi in rjDs:
            self.assertEqual(rjDi.status, task_status.SCHEDULED)
        for rjEi in rjEs:
            self.assertEqual(rjEi.status, task_status.SCHEDULED)
        for rjFi in rjFs:
            self.assertEqual(rjFi.status, task_status.SCHEDULED)

        self.assertTrue(Aout.resource.resource_file)
        for r in Bout.resource_list.resources.all():
            self.assertFalse(r.resource_file)
        self.assertFalse(Cout1.resource.resource_file)
        self.assertFalse(Cout2.resource.resource_file)
        for Douti in Douts:
            self.assertFalse(Douti.resource.resource_file)
        for Eouti in Eouts:
            self.assertFalse(Eouti.resource.resource_file)
        for Fouti in Fouts:
            for r in Fouti.resource_list.resources.all():
                self.assertFalse(r.resource_file)

        # Work with RunJob B
        response = self.client.post(
            "/api/interactive/{0}/acquire/".format(str(rjB.uuid))
        )
        # response = self.client.post(reverse("interactive-acquire", kwargs={"pk": str(rjB.uuid)}))
        assert response.status_code == status.HTTP_200_OK
        response = self.client.post(response.data["working_url"], {"foo": "bar"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # refetch
        rjA = self.test_wfjob_A.run_jobs.first()
        rjB = self.test_wfjob_B.run_jobs.first()
        rjC = self.test_wfjob_C.run_jobs.first()
        rjDs = self.test_wfjob_D.run_jobs.all()
        rjEs = self.test_wfjob_E.run_jobs.all()
        rjFs = self.test_wfjob_F.run_jobs.all()

        Aout = self.test_Aop.outputs.first()
        Bout = self.test_Bop.outputs.first()
        Cout1 = self.test_Cop1.outputs.first()
        Cout2 = self.test_Cop2.outputs.first()
        Douts = self.test_Dop.outputs.all()
        Eouts = self.test_Eop.outputs.all()
        Fouts = self.test_Fop.outputs.all()

        Ain = self.test_Aip.inputs.first()
        Cin1 = self.test_Cip1.inputs.first()
        Cin2 = self.test_Cip2.inputs.first()
        Din1s = self.test_Dip1.inputs.all()
        Din2s = self.test_Dip2.inputs.all()
        Din3s = self.test_Dip3.inputs.all()
        Ein1s = self.test_Eip1.inputs.all()
        Ein2s = self.test_Eip2.inputs.all()
        Fin1s = self.test_Fip1.inputs.all()
        Fin2s = self.test_Fip2.inputs.all()

        self.assertEqual(rjB.status, task_status.FINISHED)
        self.assertEqual(rjC.status, task_status.FINISHED)
        for rjDi in rjDs:
            self.assertEqual(rjDi.status, task_status.WAITING_FOR_INPUT)
        for rjEi in rjEs:
            self.assertEqual(rjEi.status, task_status.SCHEDULED)
        for rjFi in rjFs:
            self.assertEqual(rjFi.status, task_status.SCHEDULED)

        for r in Bout.resource_list.resources.all():
            self.assertTrue(r.resource_file)
        self.assertTrue(Cout1.resource.resource_file)
        self.assertTrue(Cout2.resource.resource_file)
        for Douti in Douts:
            self.assertFalse(Douti.resource.resource_file)
        for Eouti in Eouts:
            self.assertFalse(Eouti.resource.resource_file)
        for Fouti in Fouts:
            for r in Fouti.resource_list.resources.all():
                self.assertFalse(r.resource_file)

        # Work with one of RunJob D
        response = self.client.post(
            "/api/interactive/{0}/acquire/".format(str(rjDs[0].uuid))
        )
        assert response.status_code == status.HTTP_200_OK
        response = self.client.post(response.data["working_url"], {"foo": "bar"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # refetch
        rjA = self.test_wfjob_A.run_jobs.first()
        rjB = self.test_wfjob_B.run_jobs.first()
        rjC = self.test_wfjob_C.run_jobs.first()
        rjDs = self.test_wfjob_D.run_jobs.all()
        rjEs = self.test_wfjob_E.run_jobs.all()
        rjFs = self.test_wfjob_F.run_jobs.all()

        Aout = self.test_Aop.outputs.first()
        Bout = self.test_Bop.outputs.first()
        Cout1 = self.test_Cop1.outputs.first()
        Cout2 = self.test_Cop2.outputs.first()
        Douts = self.test_Dop.outputs.all()
        Eouts = self.test_Eop.outputs.all()
        Fouts = self.test_Fop.outputs.all()

        Ain = self.test_Aip.inputs.first()
        Cin1 = self.test_Cip1.inputs.first()
        Cin2 = self.test_Cip2.inputs.first()
        Din1s = self.test_Dip1.inputs.all()
        Din2s = self.test_Dip2.inputs.all()
        Din3s = self.test_Dip3.inputs.all()
        Ein1s = self.test_Eip1.inputs.all()
        Ein2s = self.test_Eip2.inputs.all()
        Fin1s = self.test_Fip1.inputs.all()
        Fin2s = self.test_Fip2.inputs.all()

        rjD0 = rjDs[0]
        rjDremain = rjDs[1:]

        Dout0 = rjD0.outputs.get(output_port__output_port_type__name="out_typeA")
        rjE0 = Dout0.resource.inputs.filter(run_job__workflow_job=self.test_wfjob_E)[
            0
        ].run_job
        Eout0 = rjE0.outputs.get(output_port__output_port_type__name="out_typeA")
        rjF0 = Dout0.resource.inputs.filter(run_job__workflow_job=self.test_wfjob_F)[
            0
        ].run_job
        Fout0 = rjF0.outputs.get(output_port__output_port_type__name="out_typeL")
        self.assertEqual(rjD0.status, task_status.FINISHED)
        self.assertTrue(Dout0.resource.resource_file)
        self.assertEqual(rjE0.status, task_status.FINISHED)
        self.assertTrue(Eout0.resource.resource_file)
        self.assertEqual(rjF0.status, task_status.FINISHED)
        for r in Fout0.resource_list.resources.all():
            self.assertTrue(r.resource_file)

        for rjDi in rjDremain:
            Douti = rjDi.outputs.get(output_port__output_port_type__name="out_typeA")
            rjEi = Douti.resource.inputs.filter(
                run_job__workflow_job=self.test_wfjob_E
            )[0].run_job
            Eouti = rjEi.outputs.get(output_port__output_port_type__name="out_typeA")
            rjFi = Douti.resource.inputs.filter(
                run_job__workflow_job=self.test_wfjob_F
            )[0].run_job
            Fouti = rjFi.outputs.get(output_port__output_port_type__name="out_typeL")
            self.assertEqual(rjDi.status, task_status.WAITING_FOR_INPUT)
            self.assertFalse(Douti.resource.resource_file)
            self.assertEqual(rjEi.status, task_status.SCHEDULED)
            self.assertFalse(Eouti.resource.resource_file)
            self.assertEqual(rjFi.status, task_status.SCHEDULED)
            for r in Fouti.resource_list.resources.all():
                self.assertFalse(r.resource_file)

        self.assertEqual(
            WorkflowRun.objects.get(uuid=wfrun_id).status, task_status.PROCESSING
        )

        # Work with all Runjob Ds
        for rjDi in rjDremain:
            response = self.client.post(
                "/api/interactive/{0}/acquire/".format(str(rjDi.uuid))
            )
            assert response.status_code == status.HTTP_200_OK
            response = self.client.post(response.data["working_url"], {"foo": "bar"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # refetch
        rjA = self.test_wfjob_A.run_jobs.first()  # noqa
        rjB = self.test_wfjob_B.run_jobs.first()  # noqa
        rjC = self.test_wfjob_C.run_jobs.first()  # noqa
        rjDs = self.test_wfjob_D.run_jobs.all()  # noqa
        rjEs = self.test_wfjob_E.run_jobs.all()  # noqa
        rjFs = self.test_wfjob_F.run_jobs.all()  # noqa

        Aout = self.test_Aop.outputs.first()  # noqa
        Bout = self.test_Bop.outputs.first()  # noqa
        Cout1 = self.test_Cop1.outputs.first()  # noqa
        Cout2 = self.test_Cop2.outputs.first()  # noqa
        Douts = self.test_Dop.outputs.all()  # noqa
        Eouts = self.test_Eop.outputs.all()  # noqa
        Fouts = self.test_Fop.outputs.all()  # noqa

        Ain = self.test_Aip.inputs.first()  # noqa
        Cin1 = self.test_Cip1.inputs.first()  # noqa
        Cin2 = self.test_Cip2.inputs.first()  # noqa
        Din1s = self.test_Dip1.inputs.all()  # noqa
        Din2s = self.test_Dip2.inputs.all()  # noqa
        Din3s = self.test_Dip3.inputs.all()  # noqa
        Ein1s = self.test_Eip1.inputs.all()  # noqa
        Ein2s = self.test_Eip2.inputs.all()  # noqa
        Fin1s = self.test_Fip1.inputs.all()  # noqa
        Fin2s = self.test_Fip2.inputs.all()  # noqa

        for rjDi in rjDs:
            self.assertEqual(rjDi.status, task_status.FINISHED)
        for Douti in Douts:
            self.assertTrue(Douti.resource.resource_file)
        for rjEi in rjEs:
            self.assertEqual(rjEi.status, task_status.FINISHED)
        for Eouti in Eouts:
            self.assertTrue(Eouti.resource.resource_file)
        for rjFi in rjFs:
            self.assertEqual(rjFi.status, task_status.FINISHED)
        for Fouti in Fouts:
            for r in Fouti.resource_list.resources.all():
                self.assertTrue(r.resource_file)

        self.assertEqual(
            WorkflowRun.objects.get(uuid=wfrun_id).status, task_status.FINISHED
        )


class WorkflowRunMultipleResourceCollectionsTest(
    RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin
):
    "Test workflowrun creation and execution with multiple resource collections."

    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.setUp_funnel_dummy_workflow()
        self.client.force_authenticate(user=self.test_superuser)
        response = self.client.patch(
            "/api/workflow/{0}/".format(self.test_workflow.uuid),
            {"valid": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def setUp_multiple_resource_collections(self):
        self.test_resourcecollection_a = mommy.make(
            "rodan.Resource",
            _quantity=5,
            project=self.test_project,
            resource_type=ResourceType.objects.get(mimetype="test/a1"),
        )
        self.test_resourcecollection_b = mommy.make(
            "rodan.Resource",
            _quantity=5,
            project=self.test_project,
            resource_type=ResourceType.objects.get(mimetype="test/a1"),
        )
        self.test_resourcecollection_c = mommy.make(
            "rodan.Resource",
            _quantity=5,
            project=self.test_project,
            resource_type=ResourceType.objects.get(mimetype="test/a1"),
        )
        for rc in [
            self.test_resourcecollection_a,
            self.test_resourcecollection_b,
            self.test_resourcecollection_c,
        ]:
            for index, res in enumerate(rc):
                res.name = str(index)
                res.save()
                res.resource_file.save("dummy.txt", ContentFile("dummy text"))

        return {
            self.url(self.test_Aip): list(
                map(self.url, self.test_resourcecollection_a)
            ),
            self.url(self.test_Bip): list(
                map(self.url, self.test_resourcecollection_b)
            ),
            self.url(self.test_Cip): list(
                map(self.url, self.test_resourcecollection_c)
            ),
        }

    def test_creation(self):
        ra = self.setUp_multiple_resource_collections()
        workflowrun_obj = {
            "workflow": "http://localhost:8000/api/workflow/{0}/".format(
                self.test_workflow.uuid
            ),
            "resource_assignments": ra,
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wfrun_id = response.data["uuid"]  # noqa

        self.assertEqual(self.test_wfjob_A.run_jobs.count(), 5)
        self.assertEqual(self.test_wfjob_B.run_jobs.count(), 5)
        self.assertEqual(self.test_wfjob_C.run_jobs.count(), 5)
        self.assertEqual(self.test_wfjob_D.run_jobs.count(), 5)

        self.assertEqual(self.test_Aip.inputs.count(), 5)
        self.assertEqual(self.test_Aop.outputs.count(), 5)
        self.assertEqual(self.test_Bip.inputs.count(), 5)
        self.assertEqual(self.test_Bop.outputs.count(), 5)
        self.assertEqual(self.test_Cip.inputs.count(), 5)
        self.assertEqual(self.test_Cop.outputs.count(), 5)

        self.assertEqual(self.test_Dip1.inputs.count(), 5)
        self.assertEqual(self.test_Dip2.inputs.count(), 5)
        self.assertEqual(self.test_Dip3.inputs.count(), 5)
        self.assertEqual(self.test_Dop.outputs.count(), 5)

        # Check if every set of run jobs gets the same resource name from the collections
        for Do in self.test_Dop.outputs.all():
            rjD = Do.run_job
            Di1 = rjD.inputs.get(input_port=self.test_Dip1)
            Di2 = rjD.inputs.get(input_port=self.test_Dip2)
            Di3 = rjD.inputs.get(input_port=self.test_Dip3)

            res_Ao_Di1 = Di1.resource
            res_Bo_Di2 = Di2.resource
            res_Co_Di3 = Di3.resource

            Ao = res_Ao_Di1.outputs.first()
            Bo = res_Bo_Di2.outputs.first()
            Co = res_Co_Di3.outputs.first()

            rjA = Ao.run_job
            rjB = Bo.run_job
            rjC = Co.run_job

            Ai = rjA.inputs.first()
            Bi = rjB.inputs.first()
            Ci = rjC.inputs.first()

            self.assertEqual(Ai.resource.name, Bi.resource.name)
            self.assertEqual(Ai.resource.name, Ci.resource.name)
