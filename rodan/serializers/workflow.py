import itertools
import jsonschema
from rodan.models import Workflow, WorkflowJob, InputPort, OutputPort, ResourceCollection, ResourceAssignment, Connection, Job, InputPortType, OutputPortType
from rest_framework import serializers
from rodan.serializers.workflowjob import WorkflowJobSerializer
from rodan.serializers.workflowrun import WorkflowRunSerializer
from django.core.urlresolvers import Resolver404, resolve

class WorkflowSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Workflow
        read_only_fields = ('creator', 'created', 'updated', 'workflow_jobs', 'workflow_runs')
        fields = ("url",
                  "uuid",
                  "name",
                  "project",
                  "workflow_jobs",
                  "description",
                  "created",
                  "updated",
                  "valid",
                  "workflow_runs")


class WorkflowListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Workflow
        read_only_fields = ('creator', 'created', 'updated')
        fields = ('url',
                  "uuid",
                  'project',
                  'creator',
                  'uuid',
                  'name',
                  'valid',
                  'created',
                  'updated')

    _serialized_field_name = 'serialized'

    def to_internal_value(self, data):
        if self.instance is None and self._serialized_field_name in data:
            # importing workflow
            if 'project' not in data:
                raise serializers.ValidationError({'project': ['This field is required.']})
            try:
                proj = self.fields['project'].to_internal_value(data['project'])
            except serializers.ValidationError as e:
                raise serializers.ValidationError({'project': e.detail})

            serialized = data[self._serialized_field_name]
            if not isinstance(serialized, dict):
                raise serializers.ValidationError({self._serialized_field_name: 'This field must be a JSON object.'})
            if '__version__' not in serialized:
                raise serializers.ValidationError({self._serialized_field_name: 'Please provide the version of serialization format.'})

            version = serialized['__version__']
            s_format = version_map.get(version, None)
            if s_format is None:
                raise serializers.ValidationError({self._serialized_field_name: 'Unsupported version of serialization format: {0}'.format(version)})

            try:
                s_format.validate(serialized)
            except serializers.ValidationError as e:
                raise serializers.ValidationError({self._serialized_field_name: e.detail})

            return {
                'project': proj,
                self._serialized_field_name: serialized
            }
        else:
            return super(WorkflowListSerializer, self).to_internal_value(data)

    def create(self, validated_data):
        if self._serialized_field_name in validated_data:
            # importing workflow
            serialized = validated_data[self._serialized_field_name]
            s_format = version_map[serialized['__version__']]
            return s_format.load(**validated_data)
        else:
            return super(WorkflowListSerializer, self).create(validated_data)

#################
class RodanWorkflowSerializationFormatBase(object):
    """
    Base class for Workflow Serialization and Deserialization.

    Need to override:
    - __version__ -- a float
    - schema -- a Python dictionary
    - dump(self, workflow) -> Python dictionary
    - validate_ids(self, serialized) raises self.ValidationError
    - load(self, serialized, project) -> Workflow object. Save all the related objects
      in this field.
    """

    __version__ = None
    schema = {"type": "object"}  # a basic representation. Still need to verify uniqueness and id referencing in
    ValidationError = serializers.ValidationError

    def __init__(self):
        self.schema_validator = jsonschema.Draft4Validator(self.schema)
    def dump(self, wf):
        raise NotImplementedError()
    def validate(self, serialized):
        try:
            self.schema_validator.validate(serialized)
        except jsonschema.exceptions.ValidationError as e:
            paths = []
            for i, p in enumerate(e.relative_path):
                if isinstance(p, int):   # array element
                    paths.append("[{0}]".format(p))
                else:
                    if i == 0:
                        paths.append(p)
                    else:
                        paths.append(".{0}".format(p))
            path = ''.join(paths)
            raise self.ValidationError({path: e.message})
        try:
            self.validate_extra(serialized)
        except:
            raise
    def validate_extra(self, serialized):
        raise NotImplementedError()
    def load(self, serialized, project, **k):
        raise NotImplementedError()

class RodanWorkflowSerializationFormat_v_0_1(RodanWorkflowSerializationFormatBase):
    __version__ = 0.1

    schema = {
        "type": "object",
        "required": ["__version__", "name", "workflow_jobs", "resource_collections", "connections", "resource_assignments"],
        "properties": {
            "__version__": {"type": "number"},
            "name": {"type": "string"},
            "description": {"type": "string"},
            "workflow_jobs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["input_ports", "output_ports", "job_name", "job_settings"],
                    "properties": {
                        "input_ports": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["type", "id", "label"],
                                "properties": {
                                    "type": {"type": "string"},
                                    "id": {"type": "number"},
                                    "label": {"type": "string"}
                                }
                            },
                            "uniqueItems": True
                        },
                        "output_ports": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["type", "id", "label"],
                                "properties": {
                                    "type": {"type": "string"},
                                    "id": {"type": "number"},
                                    "label": {"type": "string"}
                                }
                            },
                            "uniqueItems": True
                        },
                        "job_name": {"type": "string"},
                        "job_settings": {"type": "object"}
                    }
                },
                "uniqueItems": True
            },
            "resource_collections": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["id"],
                    "properties": {
                        "id": {"type": "number"}
                    },
                    "uniqueItems": True
                }
            },
            "connections": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["input_port", "output_port"],
                    "properties": {
                        "input_port": {"type": "number"},
                        "output_port": {"type": "number"}
                    },
                    "uniqueItems": True
                }
            },
            "resource_assignments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["input_port", "resource_collection"],
                    "properties": {
                        "input_port": {"type": "number"},
                        "resource_collection": {"type": "number"}
                    },
                    "uniqueItems": True
                }
            }
        }
    }
    def validate_extra(self, serialized):
        ip_ids = set()
        op_ids = set()
        rc_ids = set()
        for i_wfj, wfj in enumerate(serialized['workflow_jobs']):
            job_name = wfj['job_name']
            if not Job.objects.filter(job_name=job_name).exists():
                raise self.ValidationError({'workflow_jobs[{0}].job_name'.format(i_wfj): 'Job {0} does not exist in current Rodan installation.'.format(job_name)})
            for i_ip, ip in enumerate(wfj['input_ports']):
                ipt_name = ip['type']
                if not InputPortType.objects.filter(job__job_name=job_name, name=ipt_name).exists():
                    raise self.ValidationError({'workflow_jobs[{0}].input_ports[{1}].type'.format(i_wfj, i_ip): 'InputPortType {0} of Job {1} does not exist in current Rodan installation.'.format(ipt_name, job_name)})
                if ip['id'] in ip_ids:
                    raise self.ValidationError({'workflow_jobs[{0}].input_ports[{1}].id'.format(i_wfj, i_ip): 'Duplicate InputPort ID found.'})
                ip_ids.add(ip['id'])
            for i_op, op in enumerate(wfj['output_ports']):
                opt_name = op['type']
                if not OutputPortType.objects.filter(job__job_name=job_name, name=opt_name).exists():
                    raise self.ValidationError({'workflow_jobs[{0}].output_ports[{1}].type'.format(i_wfj, i_op): 'OutputPortType {0} of Job {1} does not exist in current Rodan installation.'.format(opt_name, job_name)})
                if op['id'] in op_ids:
                    raise self.ValidationError({'workflow_jobs[{0}].output_ports[{1}].id'.format(i_wfj, i_op): 'Duplicate OutputPort ID found.'})
                op_ids.add(op['id'])
            j_settings = Job.objects.get(job_name=job_name).settings
            try:
                jsonschema.Draft4Validator(j_settings).validate(wfj['job_settings'])
            except jsonschema.exceptions.ValidationError as e:
                raise self.ValidationError({'workflow_jobs[{0}].job_settings'.format(i_wfj): 'Job settings is invalid: {0}.'.format(str(e))})

        for i_rc, rc in enumerate(serialized['resource_collections']):
            if rc['id'] in rc_ids:
                raise self.ValidationError({'resource_collections[{0}]'.format(i_rc): 'Duplicate ResourceCollection ID found.'})
            rc_ids.add(rc['id'])
        for i_conn, conn in enumerate(serialized['connections']):
            if conn['input_port'] not in ip_ids:
                raise self.ValidationError({'connections[{0}].input_port'.format(i_conn): 'Referencing an invalid InputPort ID.'})
            if conn['output_port'] not in op_ids:
                raise self.ValidationError({'connections[{0}].output_port'.format(i_conn): 'Referencing an invalid OutputPort ID.'})
        for i_ra, ra in enumerate(serialized['resource_assignments']):
            if ra['input_port'] not in ip_ids:
                raise self.ValidationError({'resource_assignments[{0}].input_port'.format(i_ra): 'Referencing an invalid InputPort ID.'})
            if ra['resource_collection'] not in rc_ids:
                raise self.ValidationError({'resource_assignments[{0}].resource_collection'.format(i_ra): 'Referencing an invalid ResourceCollection ID.'})

    def dump(self, wf):
        rep = {
            '__version__': self.__version__,
            'name': wf.name,
            'workflow_jobs': [],
            'resource_collections': [],
            'connections': [],
            'resource_assignments': []
        }
        if wf.description:
            rep['description'] = wf.description

        ip_map = {}
        op_map = {}
        rc_map = {}
        ids = itertools.count(start=1, step=1)

        for i, rc in enumerate(wf.resource_collections.all()):
            rc_map[rc.uuid.hex] = ids.next()
            rep_rc = {
                'id': rc_map[rc.uuid.hex]
            }
            rep['resource_collections'].append(rep_rc)

        for wfj in wf.workflow_jobs.all():
            rep_wfj = {
                'job_name': wfj.job.job_name,
                'job_settings': wfj.job_settings,
                'input_ports': [],
                'output_ports': []
            }

            for ip in wfj.input_ports.all():
                ip_map[ip.uuid.hex] = ids.next()
                rep_ip = {
                    'label': ip.label,
                    'type': ip.input_port_type.name,
                    'id': ip_map[ip.uuid.hex]
                }
                rep_wfj['input_ports'].append(rep_ip)
                for ra in ip.resource_assignments.all():
                    rep_ra = {
                        'input_port': ip_map[ip.uuid.hex]
                    }
                    if ra.resource_collection:
                        rep_ra['resource_collection'] = rc_map[ra.resource_collection.uuid.hex]
                    elif ra.resource:
                        # transform into resource collection
                        transformed_rc_id = ids.next()
                        rep_rc = {
                            'id': transformed_rc_id
                        }
                        rep['resource_collections'].append(rep_rc)
                        rep_ra['resource_collection'] = transformed_rc_id
                    rep['resource_assignments'].append(rep_ra)

            for op in wfj.output_ports.all():
                op_map[op.uuid.hex] = ids.next()
                rep_op = {
                    'label': op.label,
                    'type': op.output_port_type.name,
                    'id': op_map[op.uuid.hex]
                }
                rep_wfj['output_ports'].append(rep_op)
            rep['workflow_jobs'].append(rep_wfj)

        for conn in Connection.objects.filter(input_port__workflow_job__workflow=wf):
            rep_conn = {
                'output_port': op_map[conn.output_port.uuid.hex],
                'input_port': ip_map[conn.input_port.uuid.hex]
            }
            rep['connections'].append(rep_conn)

        return rep

    def load(self, serialized, project, **k):
        wf = Workflow.objects.create(name=serialized['name'],
                                     project=project,
                                     description=serialized.get('description'),
                                     creator=k.get('creator'),
                                     valid=False)
        ip_map = {}
        op_map = {}
        rc_map = {}
        for rc_s in serialized['resource_collections']:
            # set up empty resource collections
            rc = ResourceCollection.objects.create(workflow=wf)
            rc_map[rc_s['id']] = rc
        for wfj_s in serialized['workflow_jobs']:
            j = Job.objects.get(job_name=wfj_s['job_name'])
            wfj = WorkflowJob.objects.create(workflow=wf,
                                             job=j,
                                             job_settings=wfj_s['job_settings'])
            for ip_s in wfj_s['input_ports']:
                ip = InputPort.objects.create(workflow_job=wfj,
                                              input_port_type=j.input_port_types.get(name=ip_s['type']),
                                              label=ip_s.get('label'))
                ip_map[ip_s['id']] = ip
            for op_s in wfj_s['output_ports']:
                op = OutputPort.objects.create(workflow_job=wfj,
                                               output_port_type=j.output_port_types.get(name=op_s['type']),
                                               label=op_s.get('label'))
                op_map[op_s['id']] = op
        for conn_s in serialized['connections']:
            conn = Connection.objects.create(output_port=op_map[conn_s['output_port']],
                                             input_port=ip_map[conn_s['input_port']])
        for ra_s in serialized['resource_assignments']:
            ra = ResourceAssignment.objects.create(resource_collection=rc_map[ra_s['resource_collection']],
                                                   input_port=ip_map[conn_s['input_port']])
        return wf


version_map = {
    0.1: RodanWorkflowSerializationFormat_v_0_1()
}
