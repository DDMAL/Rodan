from rodan.models import ResourceType
from rest_framework import serializers


class ResourceTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ResourceType
        read_only_fields = ('mimetype', 'description')
        fields = ('uuid', 'mimetype', 'description')
