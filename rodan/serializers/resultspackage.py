from rodan.models import ResultsPackage, OutputPort
from rest_framework import serializers
from rodan.serializers import AbsoluteURLField

class ResultsPackageSerializer(serializers.HyperlinkedModelSerializer):
    package_url = AbsoluteURLField(source="package_relurl", read_only=True)

    class Meta:
        model = ResultsPackage
        fields = ('url',
                  'uuid',
                  'status',
                  'percent_completed',
                  'workflow_run',
                  'packaging_mode',
                  'creator',
                  'error_summary',
                  'error_details',
                  'created',
                  'expiry_time',
                  'package_url')
        read_only_fields = ('creator', 'percent_completed', 'error_summary', 'error_details')

class ResultsPackageListSerializer(serializers.HyperlinkedModelSerializer):
    package_url = AbsoluteURLField(source="package_relurl", read_only=True)

    class Meta:
        model = ResultsPackage
        fields = ('url',
                  'uuid',
                  'status',
                  'percent_completed',
                  'workflow_run',
                  'packaging_mode',
                  'creator',
                  'error_summary',
                  'error_details',
                  'created',
                  'expiry_time',
                  'package_url')
        read_only_fields = ('creator', 'percent_completed', 'error_summary', 'error_details')
