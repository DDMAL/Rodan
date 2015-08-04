from rodan.models.workflowjobcoordinateset import WorkflowJobCoordinateSet
from rest_framework import serializers

class WorkflowJobCoordinateSetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WorkflowJobCoordinateSet
        read_only_fields = ('created', 'updated')
        fields = ("url",
                  "uuid",
                  "workflow_job",
                  "x",
                  "y",
                  "user_agent",
                  "created",
                  "updated")
