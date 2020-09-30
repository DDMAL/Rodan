import jsonschema
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from rodan.models import Workflow, InputPort, OutputPort, Job
from rodan.serializers.workflow import (
    WorkflowSerializer,
    WorkflowListSerializer,
    version_map,
)
from rodan.exceptions import CustomAPIException
from django.conf import settings

from rodan.permissions import CustomObjectPermissions


class WorkflowList(generics.ListCreateAPIView):
    """
    Returns a list of all Workflows. Accepts a POST request with a data body to
    create a new Workflow. POST requests will return the newly-created Workflow object.

    #### Other Parameters
    - `project` -- GET & POST. UUID of a Project for GET, URL of a Project for POST.
    - `name` -- POST-only.
    - `valid` -- (optional) POST-only. Should be empty string.
    """

    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    _ignore_model_permissions = True
    queryset = Workflow.objects.all()
    serializer_class = WorkflowListSerializer
    filter_fields = {
        "updated": ["lt", "gt"],
        "uuid": ["exact"],
        "created": ["lt", "gt"],
        "creator": ["exact"],
        "creator__username": ["icontains"],
        "project": ["exact"],
        "valid": ["exact"],
        "name": ["exact", "icontains"],
    }

    def perform_create(self, serializer):
        valid = serializer.validated_data.get("valid", False)
        if valid:
            raise ValidationError({
                "valid": [(
                    "You can't create a valid workflow - it must be validated through a PATCH "
                    "request."
                )]
            })

        serializer.save(creator=self.request.user)


class WorkflowDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Performs operations on a single Workflow instance.

    #### Parameters
    - `export` -- GET-only. If provided, Rodan will export the workflow into JSON format.
    - `valid` -- PATCH-only. If provided with non-empty string, workflow validation
      will be triggered.
    """

    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    _ignore_model_permissions = True
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer

    def get(self, request, *a, **k):
        if "export" in request.query_params:
            wf = self.get_object()
            serialized = version_map[
                settings.RODAN_WORKFLOW_SERIALIZATION_FORMAT_VERSION
            ].dump(wf)
            return Response(serialized)
        else:
            return super(WorkflowDetail, self).get(request, *a, **k)

    def perform_update(self, serializer):
        if "valid" in serializer.validated_data:
            to_be_validated = serializer.validated_data.get("valid", False)
            if to_be_validated:
                workflow = self.get_object()

                try:
                    self._validate(workflow)
                except WorkflowValidationError as e:

                    def object_to_url(o):
                        return reverse(
                            "{0}-detail".format(o.__class__.__name__.lower()),
                            args=[o.uuid],
                            request=self.request,
                        )

                    associated_objects_dict = {}
                    for o in e.associated_objects:
                        clsname = o.__class__.__name__.lower() + "s"
                        if clsname not in associated_objects_dict:
                            associated_objects_dict[clsname] = []
                        associated_objects_dict[clsname].append(object_to_url(o))

                    raise CustomAPIException(
                        {
                            "error_code": e.error_code,
                            "details": [e.details],
                            "associated_objects": associated_objects_dict,
                        },
                        status=status.HTTP_409_CONFLICT,
                    )
            else:
                raise ValidationError({"valid": "Cannot invalidate a Workflow."})

        serializer.save()

    def _validate(self, workflow):
        # validate WorkflowJobs
        workflow_jobs = workflow.workflow_jobs.all()
        labeler_job = Job.objects.get(name='Labeler')
        for wfjob in workflow_jobs:
            number_of_output_ports = wfjob.output_ports.count()
            if number_of_output_ports == 0 and wfjob.job_id != labeler_job.uuid:
                raise WorkflowValidationError(
                    "WFJ_NO_OP",
                    "The WorkflowJob {0} has no OutputPort.".format(wfjob.job_name),
                    [wfjob],
                )

            job = wfjob.job
            input_port_types = job.input_port_types.all()
            output_port_types = job.output_port_types.all()

            for ipt in input_port_types:
                number_of_input_ports = wfjob.input_ports.filter(
                    input_port_type=ipt
                ).count()
                if number_of_input_ports < ipt.minimum:
                    raise WorkflowValidationError(
                        "WFJ_TOO_FEW_IP",
                        "The WorkflowJob {0} has too few InputPorts of type {1}.".format(
                            wfjob.job_name, ipt.name
                        ),
                        [wfjob, ipt],
                    )
                elif number_of_input_ports > ipt.maximum:
                    raise WorkflowValidationError(
                        "WFJ_TOO_MANY_IP",
                        "The WorkflowJob {0} has too many InputPorts of type {1}.".format(
                            wfjob.job_name, ipt.name
                        ),
                        [wfjob, ipt],
                    )

            for opt in output_port_types:
                number_of_output_ports = wfjob.output_ports.filter(
                    output_port_type=opt
                ).count()
                if number_of_output_ports < opt.minimum:
                    raise WorkflowValidationError(
                        "WFJ_TOO_FEW_OP",
                        "The WorkflowJob {0} has too few OutputPorts of type {1}.".format(
                            wfjob.job_name, opt.name
                        ),
                        [wfjob, opt],
                    )
                elif number_of_output_ports > opt.maximum:
                    raise WorkflowValidationError(
                        "WFJ_TOO_MANY_OP",
                        "The WorkflowJob {0} has too many OutputPorts of type {1}.".format(
                            wfjob.job_name, opt.name
                        ),
                        [wfjob, opt],
                    )

            v = jsonschema.Draft4Validator(
                dict(job.settings)
            )  # convert JSONDict object to Python dict object.
            try:
                v.validate(wfjob.job_settings)
            except jsonschema.exceptions.ValidationError:
                raise WorkflowValidationError(
                    "WFJ_INVALID_SETTINGS",
                    "The WorkflowJob {0} has invalid settings.".format(wfjob.job_name),
                    [wfjob],
                )

        # validate InputPorts
        input_ports = InputPort.objects.filter(workflow_job__workflow=workflow)
        for ip in input_ports:
            if ip.input_port_type.job != ip.workflow_job.job:
                raise WorkflowValidationError(
                    "IP_TYPE_MISMATCH",
                    (
                        "The type of InputPort {0} is incompatible with its associated "
                        "WorkflowJob."
                    ).format(ip.label),
                    [ip],
                )

            if ip.connections.count() > 1:
                raise WorkflowValidationError(
                    "IP_TOO_MANY_CONNECTIONS",
                    "The InputPort {0} has more than one Connections".format(ip.label),
                    [ip],
                )

        # validate OutputPorts
        output_ports = OutputPort.objects.filter(workflow_job__workflow=workflow)
        for op in output_ports:
            if op.output_port_type.job != op.workflow_job.job:
                raise WorkflowValidationError(
                    "OP_TYPE_MISMATCH",
                    (
                        "The type of OutputPort {0} is incompatible with its associated "
                        "WorkflowJob."
                    ).format(op.label),
                    [op],
                )

            resource_type_set = set(op.output_port_type.resource_types.all())
            ips = []
            for connection in op.connections.all():
                ips.append(connection.input_port)
            for ip in ips:
                # check list-typed
                if ip.input_port_type.is_list and not op.output_port_type.is_list:
                    raise WorkflowValidationError(
                        "RESOURCETYPE_LIST_CONFLICT",
                        (
                            "InputPort {0} accepts a list of resources but OutputPort {1} is not "
                            "list-typed."
                        ).format(ip.label, op.label),
                        [op, ip],
                    )
                elif not ip.input_port_type.is_list and op.output_port_type.is_list:
                    raise WorkflowValidationError(
                        "RESOURCETYPE_LIST_CONFLICT",
                        "OutputPort {0} is list-typed but InputPort {1} is not.".format(
                            op.label, ip.label
                        ),
                        [op, ip],
                    )

                # then check common resource types
                in_type_set = set(ip.input_port_type.resource_types.all())
                resource_type_set = resource_type_set.intersection(in_type_set)
                if not set(resource_type_set):
                    raise WorkflowValidationError(
                        "NO_COMMON_RESOURCETYPE",
                        (
                            "There is no common ResourceType between OutputPort {0} and its "
                            "connected InputPorts."
                        ).format(op.label),
                        [op] + ips,
                    )

        # graph validation - Step 0
        if len(workflow_jobs) == 0:
            raise WorkflowValidationError("WF_EMPTY", "The Workflow is empty.", [])

        # Step 1
        self.permanent_marks_global = set()
        self.temporary_marks_global = set()

        # Step 2
        self.disjoint_set = DisjointSet(workflow_jobs)

        # Step 3&4
        for wfjob in workflow_jobs:
            try:
                if wfjob not in self.permanent_marks_global:
                    self._integrated_depth_first_search(wfjob)
            except WorkflowValidationError as e:
                raise e

        # Step 5
        one_set = self.disjoint_set.find(workflow_jobs[0])
        for wfjob in workflow_jobs:
            if self.disjoint_set.find(wfjob) is not one_set:
                raise WorkflowValidationError(
                    "WF_NOT_CONNECTED", "The Workflow is not connected."
                )

        # label all extern input/output ports
        InputPort.objects.filter(workflow_job__workflow=workflow).update(extern=False)
        OutputPort.objects.filter(workflow_job__workflow=workflow).update(extern=False)

        extern_ips_query = InputPort.objects.filter(
            workflow_job__workflow=workflow, connections__isnull=True
        )
        extern_ips_query.update(extern=True)

        extern_ops_query = OutputPort.objects.filter(
            workflow_job__workflow=workflow, connections__isnull=True
        )
        extern_ops_query.update(extern=True)

        # Valid!
        return True

    def _integrated_depth_first_search(self, this_wfjob):
        if this_wfjob in self.temporary_marks_global:
            raise WorkflowValidationError(
                "WF_HAS_CYCLES", "There is a cycle in the Workflow.", []
            )
        if this_wfjob not in self.permanent_marks_global:
            self.temporary_marks_global.add(this_wfjob)

            for op in this_wfjob.output_ports.all():
                adjacent_wfjobs = set()  # find unique adjacent nodes
                connections = op.connections.all()
                for conn in connections:
                    adj_wfjob = conn.input_port.workflow_job
                    if adj_wfjob not in adjacent_wfjobs:
                        self._integrated_depth_first_search(adj_wfjob)
                        if adj_wfjob in self.temporary_marks_global:
                            raise WorkflowValidationError(
                                "WF_HAS_CYCLES",
                                "There is a cycle in the Workflow.",
                                [conn],
                            )
                        self.disjoint_set.union(this_wfjob, adj_wfjob)
                    adjacent_wfjobs.add(adj_wfjob)

            self.permanent_marks_global.add(this_wfjob)
            self.temporary_marks_global.remove(this_wfjob)


class WorkflowValidationError(Exception):
    def __init__(self, error_code, details, associated_objects=[]):
        super(WorkflowValidationError, self).__init__()
        self.error_code = error_code
        self.details = details
        self.associated_objects = associated_objects


class DisjointSet(object):
    def __init__(self, xs):
        self._parent = {}
        # MakeSet
        for x in xs:
            self._parent[x] = x

    def find(self, x):
        parent = self._parent[x]
        if parent is x:
            return x
        else:
            new_parent = self.find(parent)
            self._parent[x] = new_parent
            return new_parent

    def union(self, x, y):
        x_root = self.find(x)
        y_root = self.find(y)
        self._parent[x_root] = y_root
