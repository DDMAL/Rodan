from rest_framework import serializers
from rodan.models.inputporttype import InputPortType


class InputPortTypeSerializer(serializers.HyperlinkedModelSerializer):
    input_port = serializers.HyperlinkedRelatedField(view_name="inputport-detail", required=False)
    input_workflow_job = serializers.HyperlinkedRelatedField(view_name="input_workflow_job", required=False)
    resource_types = serializers.PrimaryKeyRelatedField(many=True)

    class Meta:
        model = InputPortType
        fields = ("url",
                  "uuid",
                  "job",
                  "name",
                  "minimum",
                  "maximum",
                  "resource_types")
