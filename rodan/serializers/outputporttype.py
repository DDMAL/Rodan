from rest_framework import serializers
from rodan.models.outputporttype import OutputPortType


class OutputPortTypeSerializer(serializers.HyperlinkedModelSerializer):
    input_port = serializers.HyperlinkedRelatedField(view_name="inputport-detail", required=False)
    input_workflow_job = serializers.HyperlinkedRelatedField(view_name="input_workflow_job", required=False)
    resource_type = serializers.SerializerMethodField("get_resource_type")

    class Meta:
        model = OutputPortType
        fields = ("url",
                  "uuid",
                  "job",
                  "name",
                  "minimum",
                  "maximum",
                  "resource_type")

    def get_resource_type(self, obj):
        return [i for i in obj.resource_type]
