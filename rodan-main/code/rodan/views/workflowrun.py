# import urlparse
# from operator import itemgetter
# import os
# import shutil

from celery import (
    registry,
    # chain
)
# from celery.task.control import revoke
# from django.core.urlresolvers import resolve
# from django.db.models import Q
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
# from rest_framework import mixins
# from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.relations import HyperlinkedIdentityField

from rodan.models import (
    # Workflow,
    # RunJob,
    # WorkflowJob,
    WorkflowRun,
    # Connection,
    Resource,
    # Input,
    # Output,
    # OutputPort,
    InputPort,
    # ResourceType,
    ResourceList,
)
# from rodan.serializers.user import UserSerializer
from rodan.serializers.workflowrun import (
    WorkflowRunSerializer,
    # WorkflowRunByPageSerializer,
)

from rodan.constants import task_status
from rodan.exceptions import CustomAPIException
from rodan.permissions import CustomObjectPermissions


class WorkflowRunList(generics.ListCreateAPIView):
    """
    Returns a list of all WorkflowRuns. Accepts a POST request with a data body to
    create a new WorkflowRun. POST requests will return the newly-created WorkflowRun
    object.

    Creating a new WorkflowRun instance executes the workflow. Meanwhile, RunJobs,
    Inputs, Outputs and Resources are created corresponding to the workflow.

    **Parameters**

    - `workflow` -- GET & POST. UUID(GET) or Hyperlink(POST) of a Workflow.
    - `resource_assignments` -- POST-only. A JSON object. Keys are URLs of InputPorts
      in the Workflow, and values are list of Resource URLs.
    """

    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    _ignore_model_permissions = True
    queryset = WorkflowRun.objects.all()
    serializer_class = WorkflowRunSerializer
    filter_fields = {
        "status": ["exact"],
        "updated": ["lt", "gt"],
        "uuid": ["exact"],
        "workflow": ["exact"],
        "created": ["lt", "gt"],
        "project": ["exact"],
        "creator": ["exact"],
        "creator__username": ["icontains"],
        "name": ["exact", "icontains"],
    }

    def perform_create(self, serializer):
        wfrun_status = serializer.validated_data.get(
            "status", task_status.REQUEST_PROCESSING
        )
        if wfrun_status != task_status.REQUEST_PROCESSING:
            raise ValidationError(
                {"status": ["Can only create a WorkflowRun that requests processing."]}
            )

        wfrun_lrrt = serializer.validated_data.get("last_redone_runjob_tree")
        if wfrun_lrrt:
            raise ValidationError(
                {"last_redone_runjob_tree": ["Cannot set this field upon creation.."]}
            )

        wf = serializer.validated_data["workflow"]
        if not wf.valid:
            raise ValidationError(
                {"workflow": ["Workflow must be valid before you can run it."]}
            )

        if "resource_assignments" not in self.request.data:
            raise ValidationError({"resource_assignments": ["This field is required"]})
        resource_assignment_dict = self.request.data["resource_assignments"]

        try:
            validated_resource_assignment_dict = self._validate_resource_assignments(
                resource_assignment_dict, serializer
            )
        except ValidationError as e:
            e.detail = {"resource_assignments": e.detail}
            raise e

        wfrun = serializer.save(creator=self.request.user, project=wf.project)
        wf_id = str(wf.uuid)
        wfrun_id = str(wfrun.uuid)
        registry.tasks["rodan.core.create_workflowrun"].apply_async(
            (wf_id, wfrun_id, validated_resource_assignment_dict)
        )

    def _validate_resource_assignments(self, resource_assignment_dict, serializer):
        """
        Validates the resource assignments

        May throw ValidationError.
        Returns a validated dictionary.
        """
        if not isinstance(resource_assignment_dict, dict):
            raise ValidationError(["This field must be a JSON object"])

        unsatisfied_ips = set(
            InputPort.objects.filter(
                workflow_job__in=serializer.validated_data[
                    "workflow"
                ].workflow_jobs.all(),
                connections__isnull=True,
            )
        )
        validated_resource_assignment_dict = {}

        # Keep track of the collection with multiple Resources or ResourceLists
        resource_collection_length = None
        resource_collection_ip = None

        for input_port, resources in resource_assignment_dict.items():
            # 1. InputPort is not satisfied
            h_ip = HyperlinkedIdentityField(view_name="inputport-detail")
            h_ip.queryset = InputPort.objects.all()
            try:
                ip = h_ip.to_internal_value(input_port)
            except ValidationError as e:
                e.detail = {input_port: e.detail}
                raise e

            if ip not in unsatisfied_ips:
                raise ValidationError(
                    {input_port: ["Assigned InputPort must be unsatisfied"]}
                )
            unsatisfied_ips.remove(ip)
            types_of_ip = ip.input_port_type.resource_types.all()

            # 2. Resources and ResourceLists:
            if not isinstance(resources, list):
                raise ValidationError(
                    {input_port: ["A list of resources or resource lists is expected"]}
                )

            h_res = HyperlinkedIdentityField(view_name="resource-detail")
            h_res.queryset = Resource.objects.all()
            h_resl = HyperlinkedIdentityField(view_name="resourcelist-detail")
            h_resl.queryset = ResourceList.objects.all()
            ress = []

            for index, r in enumerate(resources):
                try:
                    ress.append(h_res.to_internal_value(r))  # a Resource
                except ValidationError as e:  # noqa
                    try:
                        ress.append(h_resl.to_internal_value(r))  # a ResourceList
                    except ValidationError as e:
                        e.detail = {input_port: {index: e.detail}}
                        raise e

            # No empty collection
            if len(ress) == 0:
                raise ValidationError(
                    {input_port: ["It is not allowed to assign an empty collection"]}
                )

            # Collection with multiple Resources or ResourceLists
            if len(ress) > 1:
                if resource_collection_length is None:
                    # This is the first resource collection we've encountered
                    # that has multiple items
                    resource_collection_length = len(ress)
                    resource_collection_ip = input_port
                else:
                    # Validate if the lengths are even
                    if len(ress) != resource_collection_length:
                        raise ValidationError({
                            input_port: [
                                (
                                    "The number of assigned Resources of "
                                    "ResourceLists is not even with that of {}"
                                ).format(resource_collection_ip)
                            ]
                        })

            # Resource must be in project and resource types are matched
            # If a ResourceList, it should not be empty and all individuals
            # should satisfy the above requirements.
            for index, res in enumerate(ress):
                if isinstance(res, Resource):
                    if ip.input_port_type.is_list is True:
                        raise ValidationError({
                            input_port: {
                                index: [(
                                    "The InputPort requires ResourceLists but is provided with "
                                    "Resources"
                                )]
                            }
                        })
                    if not res.resource_file:
                        raise ValidationError({
                            input_port: {
                                index: ["The resource file is not ready"]
                            }
                        })

                else:  # ResourceList
                    if ip.input_port_type.is_list is False:
                        raise ValidationError({
                            input_port: {
                                index: [(
                                    "The InputPort requires Resources but is "
                                    "provided with ResourceLists"
                                )]
                            }
                        })

                    for i, r in enumerate(res.resources.all()):
                        if not r.resource_file:
                            raise ValidationError({
                                input_port: {
                                    index: [(
                                        "The resource file of #{0} in the"
                                        "resource list is not ready").format(i)
                                    ]
                                }
                            })

                if res.project != serializer.validated_data["workflow"].project:
                    raise ValidationError({
                        input_port: {
                            index: [
                                (
                                    "Resource or ResourceList is not in the "
                                    "project of Workflow"
                                )
                            ]
                        }
                    })

                if res.resource_type is not None:
                    type_of_res = res.resource_type
                else:
                    type_of_res = res.get_resource_type()

                if type_of_res not in [x for x in types_of_ip]:
                    raise ValidationError({
                        input_port: {
                            index: [
                                (
                                    "The resource type {0} does not match the"
                                    " InputPort {1}"
                                ).format(type_of_res, types_of_ip)
                            ]
                        }
                    })

            validated_resource_assignment_dict[str(ip.uuid)] = [str(x.uuid) for x in ress]

        # Still we have unsatisfied input ports
        if unsatisfied_ips:
            raise ValidationError(
                [
                    "There are still unsatisfied InputPorts: {0}".format(
                        " ".join([h_ip.get_url(
                            port,
                            "inputport-detail",
                            self.request,
                            None
                        ) for port in unsatisfied_ips])
                    )
                ]
            )

        return validated_resource_assignment_dict


class WorkflowRunDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Performs operations on a single WorkflowRun instance.
    """

    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    _ignore_model_permissions = True
    queryset = WorkflowRun.objects.all()
    serializer_class = WorkflowRunSerializer

    def patch(self, request, *args, **kwargs):
        wfrun = self.get_object()
        old_status = wfrun.status
        new_status = request.data.get("status", None)

        serializer = self.get_serializer(wfrun, data=request.data, partial=True)
        serializer.is_valid()

        new_lrrt = serializer.validated_data.get("last_redone_runjob_tree", None)

        # validate new status
        is_cancelling_wfrun = bool(
            new_status
            and (  # noqa
                old_status in (task_status.PROCESSING, task_status.RETRYING, task_status.FAILED)  # noqa
                and new_status == task_status.REQUEST_CANCELLING  # noqa
            )
        )
        is_retrying_wfrun = bool(
            new_status
            and (  # noqa
                old_status in (task_status.CANCELLED, task_status.FAILED)  # noqa
                and new_status == task_status.REQUEST_RETRYING  # noqa
            )
        )
        if new_status and not is_cancelling_wfrun and not is_retrying_wfrun:
            raise CustomAPIException(
                {"status": ["Invalid status update"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # validate new lrrt
        is_redoing_runjob_tree = bool(new_lrrt)
        if new_lrrt:
            if new_lrrt.workflow_run != wfrun:
                raise CustomAPIException(
                    {
                        "last_redone_runjob_tree": [
                            "Requested RunJob is not in this WorkflowRun."
                        ]
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if new_lrrt.status not in (
                task_status.FINISHED,
                task_status.FAILED,
                task_status.WAITING_FOR_INPUT,
                task_status.PROCESSING,
            ):
                raise CustomAPIException(
                    {
                        "last_redone_runjob_tree": [
                            "Requested RunJob is not yet processed."
                        ]
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # let serializer validate other fields
        response = self.partial_update(
            request, *args, **kwargs
        )  # may throw validation errors
        wfrun_id = str(wfrun.uuid)

        # proceed Celery tasks
        if is_cancelling_wfrun:
            registry.tasks["rodan.core.cancel_workflowrun"].apply_async((wfrun_id,))
        elif is_retrying_wfrun:
            registry.tasks["rodan.core.retry_workflowrun"].apply_async((wfrun_id,))

        if is_redoing_runjob_tree:
            wfrun.status = task_status.REQUEST_RETRYING
            wfrun.save(update_fields=["status"])
            registry.tasks["rodan.core.redo_runjob_tree"].apply_async(
                (new_lrrt.uuid.hex,)
            )

        # HTTP response
        return response
