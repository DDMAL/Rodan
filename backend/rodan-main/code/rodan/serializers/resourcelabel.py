from rodan.models.resourcelabel import (
    ResourceLabel
)
from rest_framework import serializers


class ResourceLabelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ResourceLabel
        read_only_fields = ["uuid"]
        fields = ("url", "name", "uuid")
