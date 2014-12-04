from rodan.models.resultspackage import ResultsPackage
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
                  'output_ports',
                  'creator',
                  'error_summary',
                  'error_details',
                  'created',
                  'updated',
                  'expiry_date',
                  'package_url')
        read_only_fields = ('creator', )

class ResultsPackageListSerializer(serializers.HyperlinkedModelSerializer):
    package_url = AbsoluteURLField(source="package_relurl", read_only=True)

    class Meta:
        model = ResultsPackage
        fields = ('url',
                  'uuid',
                  'status',
                  'percent_completed',
                  'workflow_run',
                  'output_ports',
                  'creator',
                  'error_summary',
                  'error_details',
                  'created',
                  'updated',
                  'expiry_date',
                  'package_url')
        read_only_fields = ('creator', )
