"""
Permission test for Rodan.
"""
import random

from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse
from model_mommy import mommy

from rodan.constants import task_status
from rodan.models import (
    Project,
    WorkflowRun,
    Input,
    Output,
    RunJob
)
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin


# [TODO]: add test cases for creating objects that relates to non-accessible objects.
class PermissionStaticTestCase(
    RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin
):
    """
    Test case for constructing the objects using model_mommy, and access the view functions.
    """

    def setUp(self):
        self.setUp_user()
        self.test_creator = self.test_user
        self.test_admin = User.objects.create_user(
            username="test_admin", password="hahaha"
        )
        self.test_worker = User.objects.create_user(
            username="test_worker", password="hahaha"
        )
        self.test_worker2 = User.objects.create_user(
            username="test_worker2", password="hahaha"
        )
        self.test_outsider = User.objects.create_user(
            username="test_outsider", password="hahaha"
        )

    def test_all(self):
        # Set up Projects
        proj_obj = {"description": "Created Project", "name": "Another Test Project"}
        self.client.force_authenticate(user=self.test_creator)
        response = self.client.post("/api/projects/", proj_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["creator"], self.test_creator.username)
        project_pk = response.data["uuid"]
        project = Project.objects.get(pk=project_pk)

        # Add/remove admins as creator
        self.client.force_authenticate(user=self.test_creator)
        response = self.client.get(
            reverse("project-detail-admins", kwargs={"pk": project_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), set([self.test_creator.username]))

        response = self.client.patch(
            reverse("project-detail-admins", kwargs={"pk": project_pk}),
            [self.test_worker.username, self.test_outsider.username],
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data),
            set(
                [
                    self.test_creator.username,
                    self.test_worker.username,
                    self.test_outsider.username,
                ]
            ),
        )

        response = self.client.patch(
            reverse("project-detail-admins", kwargs={"pk": project_pk}),
            [self.test_admin.username],
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data),
            set([self.test_creator.username, self.test_admin.username]),
        )

        # Add/remove workers as creator
        self.client.force_authenticate(user=self.test_creator)
        response = self.client.get(
            reverse("project-detail-workers", kwargs={"pk": project_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), set([]))

        response = self.client.patch(
            reverse("project-detail-workers", kwargs={"pk": project_pk}),
            [self.test_outsider.username],
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), set([self.test_outsider.username]))

        response = self.client.patch(
            reverse("project-detail-workers", kwargs={"pk": project_pk}),
            [self.test_worker.username, self.test_worker2.username],
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data),
            set([self.test_worker.username, self.test_worker2.username]),
        )

        # Add/remove workers as admin
        self.client.force_authenticate(user=self.test_admin)
        response = self.client.get(
            reverse("project-detail-workers", kwargs={"pk": project_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data),
            set([self.test_worker.username, self.test_worker2.username]),
        )

        response = self.client.patch(
            reverse("project-detail-workers", kwargs={"pk": project_pk}),
            [self.test_worker.username],
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), set([self.test_worker.username]))

        response = self.client.patch(
            reverse("project-detail-workers", kwargs={"pk": project_pk}),
            [self.test_worker.username, self.test_worker2.username],
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data),
            set([self.test_worker.username, self.test_worker2.username]),
        )

        # No permissions to admins as admin
        self.client.force_authenticate(user=self.test_admin)
        response = self.client.get(
            reverse("project-detail-admins", kwargs={"pk": project_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(
            reverse("project-detail-admins", kwargs={"pk": project_pk}),
            [],
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Workers have no permissions to manage admins nor workers
        self.client.force_authenticate(user=self.test_worker)
        response = self.client.get(
            reverse("project-detail-admins", kwargs={"pk": project_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(
            reverse("project-detail-admins", kwargs={"pk": project_pk}),
            [],
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(
            reverse("project-detail-workers", kwargs={"pk": project_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(
            reverse("project-detail-workers", kwargs={"pk": project_pk}),
            [],
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Outsider cannot see it in Project List View, and cannot access the detail view
        self.client.force_authenticate(user=self.test_outsider)
        response = self.client.get(reverse("project-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

        response = self.client.get(reverse("project-detail", kwargs={"pk": project_pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Workers, admin, and creator can see it.
        for u in [
            self.test_worker,
            self.test_worker2,
            self.test_admin,
            self.test_creator,
        ]:
            self.client.force_authenticate(user=u)
            response = self.client.get(reverse("project-list"))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

            response = self.client.get(
                reverse("project-detail", kwargs={"pk": project_pk})
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Admins and creator can modify name and desc, but workers cannot.
        for u in [self.test_admin, self.test_creator]:
            self.client.force_authenticate(user=u)
            response = self.client.patch(
                reverse("project-detail", kwargs={"pk": project_pk}),
                {
                    "description": "new desc{0}".format(u.username),
                    "name": "new name{0}".format(u.username),
                },
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                response.data["description"], "new desc{0}".format(u.username)
            )
            self.assertEqual(response.data["name"], "new name{0}".format(u.username))

        for u in [self.test_worker, self.test_worker2]:
            self.client.force_authenticate(user=u)
            response = self.client.patch(
                reverse("project-detail", kwargs={"pk": project_pk}),
                {"description": "new desc{0}".format(u.username)},
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Admins and workers cannot delete the project
        for u in [self.test_worker, self.test_worker2, self.test_admin]:
            self.client.force_authenticate(user=u)
            response = self.client.delete(
                reverse("project-detail", kwargs={"pk": project_pk})
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Project test ends.

        # Creator, admin, and workers should be able to access(list+detail)/modify/delete the
        # objects related with the test project. Outsider cannot do that. The following codes
        # will test model-by-model.

        # Workflow
        for u in [
            self.test_worker,
            self.test_worker2,
            self.test_admin,
            self.test_creator,
        ]:
            workflow = mommy.make("rodan.Workflow", project=project)
            self.client.force_authenticate(user=u)

            response = self.client.get(reverse("workflow-list"))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

            response = self.client.get(
                reverse("workflow-detail", kwargs={"pk": workflow.pk})
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            response = self.client.patch(
                reverse("workflow-detail", kwargs={"pk": workflow.pk}),
                {"description": "new desc{0}".format(u.username)},
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                response.data["description"], "new desc{0}".format(u.username)
            )

            response = self.client.delete(
                reverse("workflow-detail", kwargs={"pk": workflow.pk}, format="json")
            )
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        workflow = mommy.make("rodan.Workflow", project=project)
        self.client.force_authenticate(user=self.test_outsider)

        response = self.client.get(reverse("workflow-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

        response = self.client.get(
            reverse("workflow-detail", kwargs={"pk": workflow.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.patch(
            reverse("workflow-detail", kwargs={"pk": workflow.pk}),
            {"description": "new desc"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete(
            reverse("workflow-detail", kwargs={"pk": workflow.pk}, format="json")
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # WorkflowJob
        for u in [
            self.test_worker,
            self.test_worker2,
            self.test_admin,
            self.test_creator,
        ]:
            workflowjob = mommy.make("rodan.WorkflowJob", workflow=workflow)
            self.client.force_authenticate(user=u)

            response = self.client.get(reverse("workflowjob-list"))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

            response = self.client.get(
                reverse("workflowjob-detail", kwargs={"pk": workflowjob.pk})
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            response = self.client.patch(
                reverse("workflowjob-detail", kwargs={"pk": workflowjob.pk}),
                {"name": "new name{0}".format(u.username)},
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["name"], "new name{0}".format(u.username))

            response = self.client.delete(
                reverse(
                    "workflowjob-detail", kwargs={"pk": workflowjob.pk}, format="json"
                )
            )
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        workflowjob = mommy.make("rodan.WorkflowJob", workflow=workflow)
        self.client.force_authenticate(user=self.test_outsider)

        response = self.client.get(reverse("workflowjob-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

        response = self.client.get(
            reverse("workflowjob-detail", kwargs={"pk": workflowjob.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.patch(
            reverse("workflowjob-detail", kwargs={"pk": workflowjob.pk}),
            {"name": "new name"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete(
            reverse("workflowjob-detail", kwargs={"pk": workflowjob.pk}, format="json")
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # InputPort
        for u in [
            self.test_worker,
            self.test_worker2,
            self.test_admin,
            self.test_creator,
        ]:
            inputport = mommy.make("rodan.InputPort", workflow_job=workflowjob)
            self.client.force_authenticate(user=u)

            response = self.client.get(reverse("inputport-list"))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

            response = self.client.get(
                reverse("inputport-detail", kwargs={"pk": inputport.pk})
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            response = self.client.patch(
                reverse("inputport-detail", kwargs={"pk": inputport.pk}),
                {"label": "new label{0}".format(u.username)},
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["label"], "new label{0}".format(u.username))

            response = self.client.delete(
                reverse("inputport-detail", kwargs={"pk": inputport.pk}, format="json")
            )
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        inputport = mommy.make("rodan.InputPort", workflow_job=workflowjob)
        self.client.force_authenticate(user=self.test_outsider)

        response = self.client.get(reverse("inputport-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

        response = self.client.get(
            reverse("inputport-detail", kwargs={"pk": inputport.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.patch(
            reverse("inputport-detail", kwargs={"pk": inputport.pk}),
            {"label": "new label"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete(
            reverse("inputport-detail", kwargs={"pk": inputport.pk}, format="json")
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # OutputPort
        for u in [
            self.test_worker,
            self.test_worker2,
            self.test_admin,
            self.test_creator,
        ]:
            outputport = mommy.make("rodan.OutputPort", workflow_job=workflowjob)
            self.client.force_authenticate(user=u)

            response = self.client.get(reverse("outputport-list"))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

            response = self.client.get(
                reverse("outputport-detail", kwargs={"pk": outputport.pk})
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            response = self.client.patch(
                reverse("outputport-detail", kwargs={"pk": outputport.pk}),
                {"label": "new label{0}".format(u.username)},
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["label"], "new label{0}".format(u.username))

            response = self.client.delete(
                reverse(
                    "outputport-detail", kwargs={"pk": outputport.pk}, format="json"
                )
            )
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        outputport = mommy.make("rodan.OutputPort", workflow_job=workflowjob)
        self.client.force_authenticate(user=self.test_outsider)

        response = self.client.get(reverse("outputport-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

        response = self.client.get(
            reverse("outputport-detail", kwargs={"pk": outputport.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.patch(
            reverse("outputport-detail", kwargs={"pk": outputport.pk}),
            {"label": "new label"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete(
            reverse("outputport-detail", kwargs={"pk": outputport.pk}, format="json")
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Connection
        outputport2 = mommy.make(
            "rodan.OutputPort", workflow_job=workflowjob
        )  # for testing
        for u in [
            self.test_worker,
            self.test_worker2,
            self.test_admin,
            self.test_creator,
        ]:
            connection = mommy.make(
                "rodan.Connection", input_port=inputport, output_port=outputport
            )
            self.client.force_authenticate(user=u)

            response = self.client.get(reverse("connection-list"))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

            response = self.client.get(
                reverse("connection-detail", kwargs={"pk": connection.pk})
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            new_op = random.choice([outputport, outputport2])
            response = self.client.patch(
                reverse("connection-detail", kwargs={"pk": connection.pk}),
                {"output_port": self.url(new_op)},
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["output_port"], self.url(new_op))

            response = self.client.delete(
                reverse(
                    "connection-detail", kwargs={"pk": connection.pk}, format="json"
                )
            )
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        connection = mommy.make(
            "rodan.Connection", input_port=inputport, output_port=outputport
        )
        self.client.force_authenticate(user=self.test_outsider)

        response = self.client.get(reverse("connection-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

        response = self.client.get(
            reverse("connection-detail", kwargs={"pk": connection.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.patch(
            reverse("connection-detail", kwargs={"pk": connection.pk}),
            {"output_port": self.url(outputport)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete(
            reverse("connection-detail", kwargs={"pk": connection.pk}, format="json")
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # # WorkflowJobCoordinateSet
        # for u in [
        #     self.test_worker,
        #     self.test_worker2,
        #     self.test_admin,
        #     self.test_creator,
        # ]:
        #     workflowjobcoordinateset = mommy.make(
        #         "rodan.Workflowjobcoordinateset", workflow_job=workflowjob
        #     )
        #     self.client.force_authenticate(user=u)

        #     response = self.client.get(reverse("workflowjobcoordinateset-list"))
        #     self.assertEqual(response.status_code, status.HTTP_200_OK)
        #     self.assertEqual(response.data["count"], 1)

        #     response = self.client.get(
        #         reverse(
        #             "workflowjobcoordinateset-detail",
        #             kwargs={"pk": workflowjobcoordinateset.pk},
        #         )
        #     )
        #     self.assertEqual(response.status_code, status.HTTP_200_OK)

        #     response = self.client.patch(
        #         reverse(
        #             "workflowjobcoordinateset-detail",
        #             kwargs={"pk": workflowjobcoordinateset.pk},
        #         ),
        #         {"user_agent": "new ua{0}".format(u.username)},
        #         format="json",
        #     )
        #     self.assertEqual(response.status_code, status.HTTP_200_OK)
        #     self.assertEqual(
        #         response.data["user_agent"], "new ua{0}".format(u.username)
        #     )

        #     response = self.client.delete(
        #         reverse(
        #             "workflowjobcoordinateset-detail",
        #             kwargs={"pk": workflowjobcoordinateset.pk},
        #             format="json",
        #         )
        #     )
        #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # workflowjobcoordinateset = mommy.make(
        #     "rodan.Workflowjobcoordinateset", workflow_job=workflowjob
        # )
        # self.client.force_authenticate(user=self.test_outsider)

        # response = self.client.get(reverse("workflowjobcoordinateset-list"))
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(response.data["count"], 0)

        # response = self.client.get(
        #     reverse(
        #         "workflowjobcoordinateset-detail",
        #         kwargs={"pk": workflowjobcoordinateset.pk},
        #     )
        # )
        # self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # response = self.client.patch(
        #     reverse(
        #         "workflowjobcoordinateset-detail",
        #         kwargs={"pk": workflowjobcoordinateset.pk},
        #     ),
        #     {"user_agent": "new ua"},
        #     format="json",
        # )
        # self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # response = self.client.delete(
        #     reverse(
        #         "workflowjobcoordinateset-detail",
        #         kwargs={"pk": workflowjobcoordinateset.pk},
        #         format="json",
        #     )
        # )
        # self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # WorkflowJobGroup

        # Resource
        for u in [
            self.test_worker,
            self.test_worker2,
            self.test_admin,
            self.test_creator,
        ]:
            resource = mommy.make("rodan.Resource", project=project)
            self.client.force_authenticate(user=u)

            response = self.client.get(reverse("resource-list"))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

            response = self.client.get(
                reverse("resource-detail", kwargs={"pk": resource.pk})
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            response = self.client.patch(
                reverse("resource-detail", kwargs={"pk": resource.pk}),
                {"description": "new desc{0}".format(u.username)},
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                response.data["description"], "new desc{0}".format(u.username)
            )

            response = self.client.delete(
                reverse("resource-detail", kwargs={"pk": resource.pk}, format="json")
            )
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        resource = mommy.make("rodan.Resource", project=project)
        self.client.force_authenticate(user=self.test_outsider)

        response = self.client.get(reverse("resource-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

        response = self.client.get(
            reverse("resource-detail", kwargs={"pk": resource.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.patch(
            reverse("resource-detail", kwargs={"pk": resource.pk}),
            {"description": "new desc"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete(
            reverse("resource-detail", kwargs={"pk": resource.pk}, format="json")
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # WorkflowRun (no delete)
        for idx, u in enumerate(
            [self.test_worker, self.test_worker2, self.test_admin, self.test_creator]
        ):
            workflowrun = mommy.make("rodan.WorkflowRun", project=project)
            self.client.force_authenticate(user=u)

            response = self.client.get(reverse("workflowrun-list"))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], idx + 1)

            response = self.client.get(
                reverse("workflowrun-detail", kwargs={"pk": workflowrun.pk})
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            response = self.client.patch(
                reverse("workflowrun-detail", kwargs={"pk": workflowrun.pk}),
                {"description": "new desc{0}".format(u.username)},
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                response.data["description"], "new desc{0}".format(u.username)
            )

        workflowrun = mommy.make("rodan.WorkflowRun", project=project)
        self.client.force_authenticate(user=self.test_outsider)

        response = self.client.get(reverse("workflowrun-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

        response = self.client.get(
            reverse("workflowrun-detail", kwargs={"pk": workflowrun.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.patch(
            reverse("workflowrun-detail", kwargs={"pk": workflowrun.pk}),
            {"description": "new desc"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # RunJob (no modify/delete)
        for idx, u in enumerate(
            [self.test_worker, self.test_worker2, self.test_admin, self.test_creator]
        ):
            runjob = mommy.make("rodan.RunJob", workflow_run=workflowrun)
            self.client.force_authenticate(user=u)

            response = self.client.get(reverse("runjob-list"))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], idx + 1)

            response = self.client.get(
                reverse("runjob-detail", kwargs={"pk": runjob.pk})
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        runjob = mommy.make("rodan.RunJob", workflow_run=workflowrun)
        self.client.force_authenticate(user=self.test_outsider)

        response = self.client.get(reverse("runjob-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

        response = self.client.get(reverse("runjob-detail", kwargs={"pk": runjob.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Input (no modify/delete)
        for idx, u in enumerate(
            [self.test_worker, self.test_worker2, self.test_admin, self.test_creator]
        ):
            input = mommy.make("rodan.Input", run_job=runjob)
            self.client.force_authenticate(user=u)

            response = self.client.get(reverse("input-list"))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], idx + 1)

            response = self.client.get(reverse("input-detail", kwargs={"pk": input.pk}))
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        input = mommy.make("rodan.Input", run_job=runjob)
        self.client.force_authenticate(user=self.test_outsider)

        response = self.client.get(reverse("input-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

        response = self.client.get(reverse("input-detail", kwargs={"pk": input.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Output (no modify/delete)
        for idx, u in enumerate(
            [self.test_worker, self.test_worker2, self.test_admin, self.test_creator]
        ):
            output = mommy.make("rodan.Output", run_job=runjob)
            self.client.force_authenticate(user=u)

            response = self.client.get(reverse("output-list"))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], idx + 1)

            response = self.client.get(
                reverse("output-detail", kwargs={"pk": output.pk})
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        output = mommy.make("rodan.Output", run_job=runjob)
        self.client.force_authenticate(user=self.test_outsider)

        response = self.client.get(reverse("output-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

        response = self.client.get(reverse("output-detail", kwargs={"pk": output.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # ResultsPackage (no modify)
        for u in [
            self.test_worker,
            self.test_worker2,
            self.test_admin,
            self.test_creator,
        ]:
            resultspackage = mommy.make(
                "rodan.ResultsPackage",
                workflow_run=workflowrun,
                status=task_status.CANCELLED,
            )
            self.client.force_authenticate(user=u)

            response = self.client.get(reverse("resultspackage-list"))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 1)

            response = self.client.get(
                reverse("resultspackage-detail", kwargs={"pk": resultspackage.pk})
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            response = self.client.delete(
                reverse(
                    "resultspackage-detail",
                    kwargs={"pk": resultspackage.pk},
                    format="json",
                )
            )
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        resultspackage = mommy.make("rodan.ResultsPackage", workflow_run=workflowrun)
        self.client.force_authenticate(user=self.test_outsider)

        response = self.client.get(reverse("resultspackage-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

        response = self.client.get(
            reverse("resultspackage-detail", kwargs={"pk": resultspackage.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete(
            reverse(
                "resultspackage-detail", kwargs={"pk": resultspackage.pk}, format="json"
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        ######################

        # Remove a worker and the admin. It should correspondingly remove all the permissions above.
        # Few ones are selected for testing.
        self.client.force_authenticate(user=self.test_creator)
        response = self.client.patch(
            reverse("project-detail-workers", kwargs={"pk": project_pk}),
            [self.test_worker.username],
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(
            reverse("project-detail-admins", kwargs={"pk": project_pk}),
            [],
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for u in [self.test_worker2, self.test_admin]:
            self.client.force_authenticate(user=u)
            response = self.client.get(reverse("resultspackage-list"))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 0)

            response = self.client.get(
                reverse("workflow-detail", kwargs={"pk": workflow.pk})
            )
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

            response = self.client.delete(
                reverse(
                    "connection-detail", kwargs={"pk": connection.pk}, format="json"
                )
            )
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Add a worker. It should correspondingly add all the permissions above.
        # Select few ones to test.
        self.client.force_authenticate(user=self.test_creator)
        response = self.client.patch(
            reverse("project-detail-workers", kwargs={"pk": project_pk}),
            [self.test_outsider.username],
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.test_outsider)
        response = self.client.get(reverse("resultspackage-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        response = self.client.get(
            reverse("workflow-detail", kwargs={"pk": workflow.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(
            reverse("connection-detail", kwargs={"pk": connection.pk}, format="json")
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class PermissionRuntimeTestCase(
    RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin
):
    """
    Test case for verifying permission in constructing workflows and executing workflowruns.
    """

    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.test_admin = User.objects.create_user(
            username="test_admin", password="hahaha"
        )
        self.test_worker = User.objects.create_user(
            username="test_worker", password="hahaha"
        )
        self.test_worker2 = User.objects.create_user(
            username="test_worker2", password="hahaha"
        )
        self.test_outsider = User.objects.create_user(
            username="test_outsider", password="hahaha"
        )

    def test_construct_workflow(self):
        """
        Scenario:
        1. The creator sets up a basic workflow.
        2. The creator adds a worker to the project.
        3. The worker adds an output port.
        4. The creator should be able to access the new output port.
        5. The creator then adds an admin to the project.
        6. The admin should be able to access the new output port created in 3.
        7. The admin then adds a new workflow job.
        8. The worker should be able to access it.
        9. The admin removes the worker.
        10. The worker should not have the access anymore.
        """
        # 1
        self.setUp_basic_workflow()
        creator = self.test_project.creator

        # 2
        self.client.force_authenticate(creator)
        response = self.client.patch(
            reverse("project-detail-workers", kwargs={"pk": self.test_project.pk}),
            [self.test_worker.username],
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3
        self.client.force_authenticate(self.test_worker)
        response = self.client.post(
            reverse("outputport-list"),
            {
                "output_port_type": reverse(
                    "outputporttype-detail", kwargs={"pk": self.test_outputporttype.pk}
                ),
                "workflow_job": reverse(
                    "workflowjob-detail", kwargs={"pk": self.test_workflowjob2.pk}
                ),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_outputport_pk = response.data["uuid"]

        # 4
        self.client.force_authenticate(creator)
        response = self.client.get(
            reverse("outputport-detail", kwargs={"pk": new_outputport_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 5
        response = self.client.patch(
            reverse("project-detail-admins", kwargs={"pk": self.test_project.pk}),
            [self.test_admin.username],
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 6
        self.client.force_authenticate(self.test_admin)
        response = self.client.get(
            reverse("outputport-detail", kwargs={"pk": new_outputport_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 7
        response = self.client.post(
            reverse("workflowjob-list"),
            {
                "job": reverse("job-detail", kwargs={"pk": self.test_job.pk}),
                "workflow": reverse(
                    "workflow-detail", kwargs={"pk": self.test_workflow.pk}
                ),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_workflowjob_pk = response.data["uuid"]

        # 8
        self.client.force_authenticate(self.test_worker)
        response = self.client.get(
            reverse("workflowjob-detail", kwargs={"pk": new_workflowjob_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 9
        self.client.force_authenticate(self.test_admin)
        response = self.client.patch(
            reverse("project-detail-workers", kwargs={"pk": self.test_project.pk}),
            [],
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 10
        self.client.force_authenticate(self.test_worker)
        response = self.client.get(
            reverse("outputport-detail", kwargs={"pk": new_outputport_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.get(
            reverse("workflowjob-detail", kwargs={"pk": new_workflowjob_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_execute_workflowrun(self):
        """
        Scenario:
        1. The creator sets up a complex workflow (as in workflowrun view test), adding an admin
            and a worker.
        2. The worker runs it.
        3. The worker, creator and admin should all have access to created WorkflowRun, RunJobs,
            Inputs, and Outputs.
        4. The worker, creator and admin should all have access to the interactive acquire view
            and interactive working view.
        5. The admin removes the worker.
        6. The worker should not have access to the components listed in 3&4 anymore.
        7. The creator removes the admin.
        8. The admin should not have access to the components listed in 3&4 anymore.
        9. The creator adds a new worker.
        10. The new worker should have access to the components listed in 3&4.
        """
        # 1
        self.setUp_complex_dummy_workflow()
        creator = self.test_project.creator
        self.client.force_authenticate(creator)
        response = self.client.patch(
            reverse("project-detail-admins", kwargs={"pk": self.test_project.pk}),
            [self.test_admin.username],
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(
            reverse("project-detail-workers", kwargs={"pk": self.test_project.pk}),
            [self.test_worker.username],
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2
        self.client.force_authenticate(self.test_worker)
        response = self.client.patch(
            "/api/workflow/{0}/".format(self.test_workflow.uuid),
            {"valid": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ra = self.setUp_resources_for_complex_dummy_workflow()
        workflowrun_obj = {
            "workflow": reverse("workflow-detail", kwargs={"pk": self.test_workflow.uuid}),
            "resource_assignments": ra,
        }
        response = self.client.post(reverse("workflowrun-list"), workflowrun_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wfrun_id = response.data["uuid"]  # noqa

        # workflowrun_update = {'status': task_status.REQUEST_PROCESSING}
        # response = self.client.patch(
        #     "/workflowrun/{0}/".format(str(wfrun_id)), workflowrun_update, format='json')
        # self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3
        counts = {
            "workflowrun": WorkflowRun.objects.all().count(),
            "runjob": RunJob.objects.all().count(),
            "input": Input.objects.all().count(),
            "output": Output.objects.all().count(),
        }
        for u in [creator, self.test_admin, self.test_worker]:
            self.client.force_authenticate(user=u)
            for k, v in counts.items():
                response = self.client.get(reverse("{0}-list".format(k)))
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data["count"], v)

        # 4
        rjB = self.test_wfjob_B.run_jobs.first()
        for u in [creator, self.test_admin, self.test_worker]:
            self.client.force_authenticate(user=u)
            rjB.working_user = None
            rjB.save(update_fields=["working_user"])
            response = self.client.post("/api/interactive/{0}/acquire/".format(rjB.pk))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response = self.client.get(response.data["working_url"])
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 5
        self.client.force_authenticate(self.test_admin)
        response = self.client.patch(
            reverse("project-detail-workers", kwargs={"pk": self.test_project.pk}),
            [],
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 6
        self.client.force_authenticate(user=self.test_worker)
        for k, v in counts.items():
            response = self.client.get(reverse("{0}-list".format(k)))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 0)

        response = self.client.post("/api/interactive/{0}/acquire/".format(rjB.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # 7
        self.client.force_authenticate(creator)
        response = self.client.patch(
            reverse("project-detail-admins", kwargs={"pk": self.test_project.pk}),
            [],
            format="json",
        )

        # 8
        self.client.force_authenticate(user=self.test_admin)
        for k, v in counts.items():
            response = self.client.get(reverse("{0}-list".format(k)))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 0)

        response = self.client.post("/api/interactive/{0}/acquire/".format(rjB.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # 9
        self.client.force_authenticate(creator)
        response = self.client.patch(
            reverse("project-detail-workers", kwargs={"pk": self.test_project.pk}),
            [self.test_worker2.username],
            format="json",
        )

        # 10
        self.client.force_authenticate(user=self.test_worker2)
        for k, v in counts.items():
            response = self.client.get(reverse("{0}-list".format(k)))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], v)

        rjB.working_user = None
        rjB.save(update_fields=["working_user"])
        response = self.client.post("/api/interactive/{0}/acquire/".format(rjB.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(response.data["working_url"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
