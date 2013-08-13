from rodan.models.resultspackage import ResultsPackage
from rest_framework import serializers


class ResultsPackageSerializer(serializers.HyperlinkedModelSerializer):

    name = serializers.Field(source='bag_name')
    workflow_run_url = serializers.HyperlinkedRelatedField(source='workflow_run', view_name='workflowrun-detail')
    page_urls = serializers.HyperlinkedRelatedField(source='pages', view_name='page-detail', many=True)
    job_urls = serializers.HyperlinkedRelatedField(source='jobs', view_name='job-detail', many=True)

    class Meta:
        model = ResultsPackage
        read_only_fields = ('created',)
        fields = ("url",
                  "workflow_run_url",
                  "name",
                  "status",
                  'percent_completed',
                  "download_url",
                  "page_urls",
                  "job_urls",
                  "creator",
                  "created",
                  "updated")


class ResultsPackageListSerializer(serializers.HyperlinkedModelSerializer):

    name = serializers.Field(source='bag_name')
    workflow_run_url = serializers.HyperlinkedRelatedField(source='workflow_run', view_name='workflowrun-detail')
    page_urls = serializers.HyperlinkedRelatedField(source='pages', view_name='page-detail', many=True)
    job_urls = serializers.HyperlinkedRelatedField(source='jobs', view_name='job-detail', many=True)

    class Meta:
        model = ResultsPackage
        read_only_fields = ('created', )
        fields = ('url',
                  'workflow_run_url',
                  'name',
                  'status',
                  'percent_completed',
                  'download_url',
                  'page_urls',
                  'job_urls',
                  'creator',
                  'created',
                  'updated')
