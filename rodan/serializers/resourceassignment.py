from rest_framework import serializers
from rodan.models import ResourceAssignment

class ResourceAssignmentSerializer(serializers.HyperlinkedModelSerializer):
    workflow = serializers.HyperlinkedRelatedField(view_name='workflow-detail', read_only=True)
    workflow_job = serializers.HyperlinkedRelatedField(view_name='workflowjob-detail', read_only=True)

    class Meta:
        model = ResourceAssignment
        fields = ("url",
                  "uuid",
                  "input_port",
                  "resource",
                  "resource_collection",
                  "workflow",
                  "workflow_job")

    def validate(self, data):
        if self.partial:
            r = data.get('resource', self.instance.resource)
            rc = data.get('resource_collection', self.instance.resource_collection)
            ip = data.get('input_port', self.instance.input_port)
        else:
            r = data.get('resource', None)
            rc = data.get('resource_collection', None)
            ip = data['input_port']

        if not r and not rc:
            raise serializers.ValidationError("The ResourceAssignment should have either one Resource or one ResourceCollection.")
        elif r and rc:
            raise serializers.ValidationError("The ResourceAssignment should not have both Resource and ResourceCollection.")

        if r:
            if r.project != ip.workflow_job.workflow.project:
                raise serializers.ValidationError("The InputPort is not in the same project as Resource.")
        elif rc:
            if rc.workflow != ip.workflow_job.workflow:
                raise serializers.ValidationError("The InputPort is not in the same workflow as ResourceCollection.")

        return data
