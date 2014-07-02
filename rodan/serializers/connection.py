from rest_framework import serializers
from rodan.models.connection import Connection


class ConnectionSerializer(serializers.HyperlinkedModelSerializer):
    input_port = serializers.HyperlinkedRelatedField(view_name="inputport-detail", required=False)

    class Meta:
        model = Connection
        fields = ("url",
                  "input_port",
                  "input_workflow_job",
                  "output_port",
                  "output_workflow_job",
                  "workflow")
