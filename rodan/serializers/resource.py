from rodan.models.resource import Resource
from rest_framework import serializers
from rodan.serializers.user import UserListSerializer
from rodan.serializers.output import OutputSerializer


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.HyperlinkedRelatedField(view_name="project-detail")
    creator = UserListSerializer(read_only=True)
    uuid = serializers.Field(source='uuid')
    origin = OutputSerializer()

    class Meta:
        model = Resource
        read_only_fields = ('created', 'updated')
        fields = ("url",
                  "uuid",
                  "project",
                  "name",
                  "creator",
                  "origin",
                  "created",
                  "updated")
