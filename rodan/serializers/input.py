from rest_framework import serializers
from rodan.models.input import Input
from rodan.serializers.user import UserListSerializer
from rodan.serializers.resource import ResourceSerializer
from rodan.serializers.inputport import InputPortSerializer
from rodan.serializers.runjob import RunJobSerializer


class InputSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserListSerializer(read_only=True)
    resource = ResourceSerializer()
    run_job = RunJobSerializer()
    input_port = InputPortSerializer()

    class Meta:
        model = Input
        fields = ("url",
                  "uuid",
                  "input_port",
                  "run_job",
                  "resource")
