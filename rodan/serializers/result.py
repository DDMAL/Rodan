from rodan.models.result import Result
from rest_framework import serializers
from rodan.serializers.runjob import RunJobSerializer


class ResultSerializer(serializers.HyperlinkedModelSerializer):
    run_job = RunJobSerializer()
    result = serializers.FileField(allow_empty_file=True)

    class Meta:
        model = Result
        read_only_fields = ('created', 'updated')
        fields = ("url", "result", "run_job", "created", "updated")
