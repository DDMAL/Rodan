from rodan.models.result import Result
from rest_framework import serializers
# from rodan.serializers.runjob import RunJobSerializer


class ResultSerializer(serializers.HyperlinkedModelSerializer):
    # run_job = RunJobSerializer()
    result = serializers.FileField(allow_empty_file=True)
    small_thumb_url = serializers.Field(source="small_thumb_url")
    medium_thumb_url = serializers.Field(source="medium_thumb_url")
    large_thumb_url = serializers.Field(source="large_thumb_url")

    class Meta:
        model = Result
        read_only_fields = ('created', 'updated')
        fields = ("url",
                  "result",
                  "run_job",
                  "small_thumb_url",
                  "medium_thumb_url",
                  "large_thumb_url",
                  "created",
                  "updated")
