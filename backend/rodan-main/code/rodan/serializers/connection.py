from rest_framework import serializers
from rodan.models.connection import Connection


class ConnectionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Connection
        fields = (
            "url",
            "uuid",
            "input_port",
            "output_port",
            "offset_x",
            "offset_y",
        )

    def validate(self, data):
        if self.partial:
            ip = data.get("input_port", self.instance.input_port)
            op = data.get("output_port", self.instance.output_port)
        else:
            ip = data["input_port"]
            op = data["output_port"]

        if ip.workflow_job.workflow != op.workflow_job.workflow:
            raise serializers.ValidationError(
                "The InputPort is not in the same workflow as the OutputPort."
            )

        return data
