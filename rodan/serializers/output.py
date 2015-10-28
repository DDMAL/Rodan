from rest_framework import serializers
from rodan.models.output import Output
from rodan.serializers.user import UserListSerializer
from rodan.serializers.outputport import OutputPortSerializer
from rodan.serializers.runjob import RunJobSerializer


class OutputSerializer(serializers.HyperlinkedModelSerializer):
    output_port_type = serializers.HyperlinkedRelatedField(view_name='outputporttype-detail', read_only=True, lookup_field="uuid", lookup_url_kwarg="pk")
    class Meta:
        model = Output
        fields = ("url",
                  "uuid",
                  "output_port_type_name",
                  "output_port_type",
                  "run_job",
                  "resource")


class OutputListSerializer(serializers.HyperlinkedModelSerializer):
    output_port_type = serializers.HyperlinkedRelatedField(view_name='outputporttype-detail', read_only=True, lookup_field="uuid", lookup_url_kwarg="pk")
    class Meta:
        model = Output
        fields = ("url",
                  "uuid",
                  "output_port_type_name",
                  "output_port_type",
                  "run_job",
                  "resource")
