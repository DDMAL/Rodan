from rodan.models.workflowjobgroupcoordinateset import WorkflowJobGroupCoordinateSet
from rest_framework import serializers
from rodan.serializers import TransparentField

class WorkflowJobGroupCoordinateSetSerializer(serializers.HyperlinkedModelSerializer):
    data = TransparentField(required=False)

    class Meta:
        model = WorkflowJobGroupCoordinateSet
        read_only_fields = ('created', 'updated')
        fields = ("url",
                  "uuid",
                  "workflow_job_group",
                  "data",
                  "user_agent",
                  "created",
                  "updated")
