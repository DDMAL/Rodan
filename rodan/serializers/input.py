from rest_framework import serializers
from rodan.models.input import Input
from rodan.serializers.user import UserListSerializer
from rodan.serializers.resource import ResourceSerializer
from rodan.serializers.inputport import InputPortSerializer
from rodan.serializers.runjob import RunJobSerializer


class InputSerializer(serializers.HyperlinkedModelSerializer):
    input_port_type = serializers.HyperlinkedRelatedField(view_name='inputporttype-detail', read_only=True)
    class Meta:
        model = Input
        fields = ("url",
                  "uuid",
                  "input_port_type_name",
                  "input_port_type",
                  "run_job",
                  "resource")
