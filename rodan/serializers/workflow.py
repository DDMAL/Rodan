import itertools
import jsonschema
from rodan.models import (
    Workflow,
    WorkflowJob,
    InputPort,
    OutputPort,
    Connection,
    Job,
    InputPortType,
    OutputPortType,
    Project,
    WorkflowJobGroup,
)
from rodan.serializers.inputport import InputPortSerializer
from rodan.serializers.outputport import OutputPortSerializer
from rodan.serializers.workflowjob import WorkflowJobSerializer
from rest_framework import serializers
from django.conf import settings


class WorkflowSerializer(serializers.HyperlinkedModelSerializer):
    workflow_jobs = WorkflowJobSerializer(many=True, read_only=True)
    workflow_input_ports = InputPortSerializer(many=True, read_only=True)
    workflow_output_ports = OutputPortSerializer(many=True, read_only=True)
    creator = serializers.SlugRelatedField(slug_field="username", read_only=True)

    def validate_project(self, p):
        # [TODO] This should be applied to all objects. It prevents an outsider
        # creating objects related to the Project, although normally the outsider
        # shouldn't know the UUID of the Project as the Project doesn't appear
        # in the list view. So it's fine in most cases.
        user = self.context["request"].user
        if not user.has_perm("view_project", p):
            raise serializers.ValidationError("You have no permissions to it.")
        return p

    class Meta:
        model = Workflow
        read_only_fields = (
            "creator",
            "created",
            "updated",
            "workflow_jobs",
            "workflow_runs",
            "workflow_input_ports",
            "workflow_output_ports",
            "project",
        )
        fields = (
            "url",
            "uuid",
            "name",
            "project",
            "workflow_jobs",
            "description",
            "created",
            "updated",
            "creator",
            "valid",
            "workflow_runs",
            "workflow_input_ports",
            "workflow_output_ports",
        )


class WorkflowListSerializer(serializers.HyperlinkedModelSerializer):
    creator = serializers.SlugRelatedField(slug_field="username", read_only=True)

    def validate_project(self, p):
        # [TODO] This should be applied to all objects. It prevents an outsider
        # creating objects related to the Project, although normally the outsider
        # shouldn't know the UUID of the Project as the Project doesn't appear
        # in the list view. So it's fine in most cases.
        user = self.context["request"].user
        if not user.has_perm("view_project", p):
            raise serializers.ValidationError("You have no permissions to it.")
        return p

    class Meta:
        model = Workflow
        read_only_fields = ("creator", "created", "updated")
        fields = (
            "url",
            "uuid",
            "project",
            "description",
            "creator",
            "uuid",
            "name",
            "valid",
            "created",
            "updated",
        )

    _serialized_field_name = "serialized"

    def to_internal_value(self, data):
        if (
            self.instance is None and self._serialized_field_name in data
        ):  # creating: self.instance is None
            # importing workflow
            if "project" not in data:
                raise serializers.ValidationError(
                    {"project": ["This field is required."]}
                )
            try:
                proj = self.fields["project"].to_internal_value(data["project"])
            except serializers.ValidationError as e:
                raise serializers.ValidationError({"project": e.detail})

            serialized = data[self._serialized_field_name]
            if not isinstance(serialized, dict):
                raise serializers.ValidationError(
                    {self._serialized_field_name: "This field must be a JSON object."}
                )
            if "__version__" not in serialized:
                raise serializers.ValidationError({
                    self._serialized_field_name:
                    "Please provide the version of serialization format."
                })

            version = serialized["__version__"]
            s_format = version_map.get(version, None)
            if s_format is None:
                raise serializers.ValidationError({
                    self._serialized_field_name:
                    "Unsupported version of serialization format: {0}".format(version)
                })

            try:
                s_format.validate(serialized)
            except serializers.ValidationError as e:
                raise serializers.ValidationError(
                    {self._serialized_field_name: e.detail}
                )

            return {"project": proj, self._serialized_field_name: serialized}
        elif self.instance is None and "workflow_job_group" in data:
            if "project" not in data:
                raise serializers.ValidationError(
                    {"project": ["This field is required."]}
                )
            try:
                proj = self.fields["project"].to_internal_value(data["project"])
            except serializers.ValidationError as e:
                raise serializers.ValidationError({"project": e.detail})

            wfjgroup_field = serializers.HyperlinkedRelatedField(
                view_name="workflowjobgroup-detail",
                queryset=WorkflowJobGroup.objects.all(),
                write_only=True,
                lookup_field="uuid",
                lookup_url_kwarg="pk",
            )
            try:
                wfjgroup = wfjgroup_field.to_internal_value(data["workflow_job_group"])
            except serializers.ValidationError as e:
                raise serializers.ValidationError({"workflow_job_group": e.detail})

            return {"project": proj, "workflow_job_group": wfjgroup}
        else:
            return super(WorkflowListSerializer, self).to_internal_value(data)

    def create(self, validated_data):
        if self._serialized_field_name in validated_data:
            # importing workflow
            serialized = validated_data[self._serialized_field_name]
            s_format = version_map[serialized["__version__"]]
            return s_format.load(
                serialized,
                self.validated_data["project"],
                creator=self.context["request"].user,
            )
        elif "workflow_job_group" in validated_data:
            # exporting wfjgroup
            dumped_wfjs = version_map[
                settings.RODAN_WORKFLOW_SERIALIZATION_FORMAT_VERSION
            ].dump(self.validated_data["workflow_job_group"])
            loaded_wf = version_map[
                settings.RODAN_WORKFLOW_SERIALIZATION_FORMAT_VERSION
            ].load(
                dumped_wfjs,
                self.validated_data["project"],
                creator=self.context["request"].user,
            )
            return loaded_wf
        else:
            return super(WorkflowListSerializer, self).create(validated_data)


#################
class RodanWorkflowSerializationFormatBase(object):
    """
    Base class for Workflow Serialization and Deserialization.
    [TODO]: refactor the serialization API to better handle wfjgroup-related dump/load.

    Need to override:
    - __version__ -- a float
    - schema -- a Python dictionary
    - dump(self, workflow_or_wfjgroup) -> Python dictionary
    - validate_ids(self, serialized) raises self.ValidationError
    - load(self, serialized, project_or_workflow) -> Workflow object. Save all the related objects
      in this field.
    """

    __version__ = None
    schema = {
        "type": "object"
    }  # a basic representation. Still need to verify uniqueness and id referencing in
    ValidationError = serializers.ValidationError

    def __init__(self):
        self.schema_validator = jsonschema.Draft4Validator(self.schema)

    def dump(self, wf_or_wfjgroup):
        raise NotImplementedError()

    def validate(self, serialized):
        try:
            self.schema_validator.validate(serialized)
        except jsonschema.exceptions.ValidationError as e:
            paths = []
            for i, p in enumerate(e.relative_path):
                if isinstance(p, int):  # array element
                    paths.append("[{0}]".format(p))
                else:
                    if i == 0:
                        paths.append(p)
                    else:
                        paths.append(".{0}".format(p))
            path = "".join(paths)
            raise self.ValidationError({path: e.message})
        try:
            self.validate_extra(serialized)
        except:  # noqa
            raise

    def validate_extra(self, serialized):
        raise NotImplementedError()

    def load(self, serialized, project_or_workflow, **k):
        raise NotImplementedError()


class RodanWorkflowSerializationFormat_v_0_1(RodanWorkflowSerializationFormatBase):
    __version__ = 0.1

    schema = {
        "type": "object",
        "required": [
            "__version__",
            "name",
            "description",
            "workflow_jobs",
            "connections",
        ],
        "properties": {
            "__version__": {"type": "number"},
            "name": {"type": "string"},
            "description": {"type": "string"},
            "workflow_jobs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": [
                        "input_ports",
                        "output_ports",
                        "job_name",
                        "job_settings",
                    ],
                    "properties": {
                        "input_ports": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["type", "id", "label"],
                                "properties": {
                                    "type": {"type": "string"},
                                    "id": {"type": "number"},
                                    "label": {"type": "string"},
                                },
                            },
                            "uniqueItems": True,
                        },
                        "output_ports": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["type", "id", "label"],
                                "properties": {
                                    "type": {"type": "string"},
                                    "id": {"type": "number"},
                                    "label": {"type": "string"},
                                },
                            },
                            "uniqueItems": True,
                        },
                        "job_name": {"type": "string"},
                        "job_settings": {"type": "object"},
                    },
                },
                "uniqueItems": True,
            },
            "connections": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["input_port", "output_port"],
                    "properties": {
                        "input_port": {"type": "number"},
                        "output_port": {"type": "number"},
                    },
                    "uniqueItems": True,
                },
            },
        },
    }

    def validate_extra(self, serialized):
        ip_ids = set()
        op_ids = set()
        # rc_ids = set()
        for i_wfj, wfj in enumerate(serialized["workflow_jobs"]):
            job_name = wfj["job_name"]
            if not Job.objects.filter(name=job_name).exists():
                raise self.ValidationError(
                    {
                        "workflow_jobs[{0}].job_name".format(
                            i_wfj
                        ): "Job {0} does not exist in current Rodan installation.".format(
                            job_name
                        )
                    }
                )
            for i_ip, ip in enumerate(wfj["input_ports"]):
                ipt_name = ip["type"]
                if not InputPortType.objects.filter(
                    job__name=job_name, name=ipt_name
                ).exists():
                    raise self.ValidationError({
                        "workflow_jobs[{0}].input_ports[{1}].type".format(i_wfj, i_ip):
                        (
                            "InputPortType {0} of Job {1} does not exist in current Rodan "
                            "installation."
                        ).format(ipt_name, job_name)
                    })
                if ip["id"] in ip_ids:
                    raise self.ValidationError(
                        {
                            "workflow_jobs[{0}].input_ports[{1}].id".format(
                                i_wfj, i_ip
                            ): "Duplicate InputPort ID found."
                        }
                    )
                ip_ids.add(ip["id"])
            for i_op, op in enumerate(wfj["output_ports"]):
                opt_name = op["type"]
                if not OutputPortType.objects.filter(
                    job__name=job_name, name=opt_name
                ).exists():
                    raise self.ValidationError({
                        "workflow_jobs[{0}].output_ports[{1}].type".format(i_wfj, i_op):
                        (
                            "OutputPortType {0} of Job {1} does not exist in current "
                            "Rodan installation."
                        ).format(opt_name, job_name)
                    })
                if op["id"] in op_ids:
                    raise self.ValidationError({
                        "workflow_jobs[{0}].output_ports[{1}].id".format(i_wfj, i_op):
                        "Duplicate OutputPort ID found."
                    })
                op_ids.add(op["id"])
            j_settings = Job.objects.get(name=job_name).settings
            try:
                jsonschema.Draft4Validator(j_settings).validate(wfj["job_settings"])
            except jsonschema.exceptions.ValidationError as e:
                raise self.ValidationError(
                    {
                        "workflow_jobs[{0}].job_settings".format(
                            i_wfj
                        ): "Job settings is invalid: {0}.".format(str(e))
                    }
                )

        for i_conn, conn in enumerate(serialized["connections"]):
            if conn["input_port"] not in ip_ids:
                raise self.ValidationError(
                    {
                        "connections[{0}].input_port".format(
                            i_conn
                        ): "Referencing an invalid InputPort ID."
                    }
                )
            if conn["output_port"] not in op_ids:
                raise self.ValidationError(
                    {
                        "connections[{0}].output_port".format(
                            i_conn
                        ): "Referencing an invalid OutputPort ID."
                    }
                )

    def dump(self, wf_or_wfjgroup):
        if isinstance(wf_or_wfjgroup, Workflow):
            wf = wf_or_wfjgroup
            wfjgroup = None
            name = wf.name
            description = wf.description or ""
        elif isinstance(wf_or_wfjgroup, WorkflowJobGroup):
            wfjgroup = wf_or_wfjgroup
            wf = wfjgroup.workflow
            name = wfjgroup.name
            description = wfjgroup.description or ""
        else:
            raise TypeError("dump(wf_or_wfjgroup) receives a wrong type of argument.")

        rep = {
            "__version__": self.__version__,
            "name": name,
            "description": description,
            "workflow_jobs": [],
            "connections": [],
        }

        ip_map = {}
        op_map = {}
        ids = itertools.count(start=1, step=1)

        wfj_queryset = (
            wf.workflow_jobs.all() if wfjgroup is None else wfjgroup.workflow_jobs.all()
        )
        for wfj in wfj_queryset:
            rep_wfj = {
                "job_name": wfj.job.name,
                "job_settings": wfj.job_settings,
                "input_ports": [],
                "output_ports": [],
            }

            for ip in wfj.input_ports.all():
                ip_map[ip.uuid.hex] = ids.next()
                rep_ip = {
                    "label": ip.label,
                    "type": ip.input_port_type.name,
                    "id": ip_map[ip.uuid.hex],
                }
                rep_wfj["input_ports"].append(rep_ip)

            for op in wfj.output_ports.all():
                op_map[op.uuid.hex] = ids.next()
                rep_op = {
                    "label": op.label,
                    "type": op.output_port_type.name,
                    "id": op_map[op.uuid.hex],
                }
                rep_wfj["output_ports"].append(rep_op)
            rep["workflow_jobs"].append(rep_wfj)

        if wfjgroup is None:
            conn_queryset = Connection.objects.filter(
                input_port__workflow_job__workflow=wf
            )
        else:
            wfj_pks = list(wfj_queryset.values_list("pk", flat=True))
            conn_queryset = Connection.objects.filter(
                input_port__workflow_job__in=wfj_pks,
                output_port__workflow_job__in=wfj_pks,
            )
        for conn in conn_queryset:
            rep_conn = {
                "output_port": op_map[conn.output_port.uuid.hex],
                "input_port": ip_map[conn.input_port.uuid.hex],
            }
            rep["connections"].append(rep_conn)

        return rep

    def load(self, serialized, project_or_workflow, **k):
        if isinstance(project_or_workflow, Project):
            wf = Workflow.objects.create(
                name=serialized["name"],
                project=project_or_workflow,
                description=serialized["description"],
                creator=k.get("creator"),
                valid=False,
            )
            loaded_wfjs = []
        elif isinstance(project_or_workflow, Workflow):
            wf = project_or_workflow
            loaded_wfjs = []
        else:
            raise TypeError(
                "load(serialized, project_or_workflow, **k) receives a wrong type of argument."
            )
        ip_map = {}
        op_map = {}

        for wfj_s in serialized["workflow_jobs"]:
            j = Job.objects.get(name=wfj_s["job_name"])
            wfj = WorkflowJob.objects.create(
                workflow=wf, job=j, job_settings=wfj_s["job_settings"]
            )
            for ip_s in wfj_s["input_ports"]:
                ip = InputPort.objects.create(
                    workflow_job=wfj,
                    input_port_type=j.input_port_types.get(name=ip_s["type"]),
                    label=ip_s.get("label"),
                )
                ip_map[ip_s["id"]] = ip
            for op_s in wfj_s["output_ports"]:
                op = OutputPort.objects.create(
                    workflow_job=wfj,
                    output_port_type=j.output_port_types.get(name=op_s["type"]),
                    label=op_s.get("label"),
                )
                op_map[op_s["id"]] = op
            loaded_wfjs.append(wfj)
        for conn_s in serialized["connections"]:
            conn = Connection.objects.create(  # noqa
                output_port=op_map[conn_s["output_port"]],
                input_port=ip_map[conn_s["input_port"]],
            )

        if isinstance(project_or_workflow, Project):
            return wf
        elif isinstance(project_or_workflow, Workflow):
            return loaded_wfjs


version_map = {0.1: RodanWorkflowSerializationFormat_v_0_1()}
