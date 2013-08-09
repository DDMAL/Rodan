from rodan.models.result import Result
from rest_framework import serializers
# from rodan.serializers.runjob import RunJobSerializer


class ResultSerializer(serializers.HyperlinkedModelSerializer):
    # run_job = RunJobSerializer()
    result = serializers.Field(source="image_url")
    small_thumb_url = serializers.Field(source="small_thumb_url")
    medium_thumb_url = serializers.Field(source="medium_thumb_url")
    large_thumb_url = serializers.Field(source="large_thumb_url")
    run_job_name = serializers.Field(source="run_job_name")

    class Meta:
        model = Result
        read_only_fields = ('created', 'updated')
        fields = ("url",
                  "result",
                  "run_job",
                  "run_job_name",
                  "small_thumb_url",
                  "medium_thumb_url",
                  "large_thumb_url",
                  "created",
                  "updated",
                  "processed")
