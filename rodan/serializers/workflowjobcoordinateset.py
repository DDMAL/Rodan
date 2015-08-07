from rodan.models.workflowjobcoordinateset import WorkflowJobCoordinateSet
from rest_framework import serializers
from rodan.serializers import TransparentField

class WorkflowJobCoordinateSetSerializer(serializers.HyperlinkedModelSerializer):
    data = TransparentField(required=False)

    class Meta:
        model = WorkflowJobCoordinateSet
        read_only_fields = ('created', 'updated')
        fields = ("url",
                  "uuid",
                  "workflow_job",
                  "data",
                  "user_agent",
                  "created",
                  "updated")
