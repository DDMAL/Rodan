from rodan.models.resource import Resource
from rest_framework import serializers
from rodan.serializers.user import UserListSerializer


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.HyperlinkedRelatedField(view_name="project-detail")
    creator = UserListSerializer(read_only=True)
    uuid = serializers.Field(source='uuid')
    origin = serializers.HyperlinkedRelatedField(view_name="output-detail")

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


class OutputResourceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Resource
