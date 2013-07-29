from rodan.models.resultspackage import ResultsPackage
from rest_framework import serializers


class ResultsPackageSerializer(serializers.HyperlinkedModelSerializer):

    name = serializers.Field(source='bag_name')

    class Meta:
        model = ResultsPackage
        read_only_fields = ('created',)
        fields = ("url",
                  "name",
                  "status",
                  'percent_completed',
                  "download_url",
                  "workflow_run",
                  "pages",
                  "jobs",
                  "creator",
                  "created",
                  "updated")


class ResultsPackageListSerializer(serializers.HyperlinkedModelSerializer):

    name = serializers.Field(source='bag_name')

    class Meta:
        model = ResultsPackage
        read_only_fields = ('created', )
        fields = ('url',
                  'name',
                  'workflow_run',
                  'download_url',
                  'status',
                  'creator',
                  'created',
                  'updated')
