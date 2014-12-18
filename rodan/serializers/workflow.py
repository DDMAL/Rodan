from rodan.models import Workflow, WorkflowJob, InputPort, OutputPort, ResourceCollection, ResourceAssignment, Connection, Job
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
                validated_serialized = s_format.validate(serialized)
            except ValueError as e:
                raise serializers.ValidationError({self._serialized_field_name: str(e)})

            return {
                'project': proj,
                self._serialized_field_name: validated_serialized
            }
        else:
            return super(WorkflowSerializer, self).to_internal_value(data)

    def create(self, validated_data):
        if self._serialized_field_name in validated_data:
            # importing workflow
            serialized = validated_data[self._serialized_field_name]
            s_format = version_map[serialized['__version__']]
            return s_format.load(**validated_data)
        else:
            return super(WorkflowSerializer, self).create(validated_data)

#################
class RodanWorkflowSerializationFormatBase(object):
    __version__ = None
    def dump(self, wf):
        raise NotImplementedError()
    def validate(self, data):
        raise NotImplementedError()
    def load(self, serialized, project, **k):
        raise NotImplementedError()

class RodanWorkflowSerializationFormat_v_0_1(RodanWorkflowSerializationFormatBase):
    __version__ = 0.1

    def dump(self, wf):
        rep = {
            '__version__': self.__version__,
            'name': wf.name,
            'description': wf.description,
            'workflow_jobs': [],
            'resource_collections': [],
            'connections': [],
            'resource_assignments': []
        }
        for rc in wf.resource_collections.all():
            rep_rc = {
                'id': rc.uuid.hex
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
                rep_ip = {
                    'label': ip.label,
                    'type': ip.input_port_type.name,
                    'id': ip.uuid.hex
                }
                rep_wfj['input_ports'].append(rep_ip)
                for ra in ip.resource_assignments.all():
                    rep_ra = {
                        'input_port': ip.uuid.hex
                    }
                    if ra.resource_collection:
                        rep_ra['resource_collection'] = ra.resource_collection.uuid.hex
                    elif ra.resource:
                        # transform into resource collection
                        transformed_rc_id = uuid.uuid1().hex
                        rep_rc = {
                            'id': transformed_rc_id
                        }
                        rep['resource_collection'].append(rep_rc)
                        rep_ra['resource_collection'] = transformed_rc_id
                    rep['resource_assignments'].append(rep_ra)

            for op in wfj.output_ports.all():
                rep_op = {
                    'label': op.label,
                    'type': op.output_port_type.name,
                    'id': op.uuid.hex
                }
                rep_wfj['output_ports'].append(rep_op)
                for conn in op.connections.all():
                    rep_conn = {
                        'output_port': conn.output_port.uuid.hex,
                        'input_port': conn.input_port.uuid.hex
                    }
                    rep['connections'].append(rep_conn)
            rep['workflow_jobs'].append(rep_wfj)

        return rep

    def validate(self, serialized):
        # [TODO] raise errors
        return serialized

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
