from rest_framework import serializers
from rodan.models.input import Input


class InputSerializer(serializers.HyperlinkedModelSerializer):
    input_port_type = serializers.HyperlinkedRelatedField(view_name='inputporttype-detail', read_only=True, lookup_field="uuid", lookup_url_kwarg="pk")
    class Meta:
        model = Input
        fields = ("url",
                  "uuid",
                  "input_port_type_name",
                  "input_port_type",
                  "run_job",
                  "resource")
