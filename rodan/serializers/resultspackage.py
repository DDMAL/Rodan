from rodan.models.resultspackage import ResultsPackage
from rest_framework import serializers


class ResultsPackageSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.Field(source='bag_name')
    class Meta:
        model = ResultsPackage
        read_only_fields = ('created', 'status', 'percent_completed', 'download_url')
        fields = ("url",
                  "workflow_run_url",
                  "name",
                  "status",
                  'percent_completed',
                  "download_url",
                  "job_urls",
                  "creator",
                  "created",
                  "updated")


class ResultsPackageListSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.Field(source='bag_name')
    class Meta:
        model = ResultsPackage
        read_only_fields = ('created', 'status', 'percent_completed', 'download_url')
        fields = ('url',
                  'workflow_run_url',
                  'name',
                  'status',
                  'percent_completed',
                  'download_url',
                  'job_urls',
                  'creator',
                  'created',
                  'updated')
