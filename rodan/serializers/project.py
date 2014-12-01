from rodan.models.project import Project
from rest_framework import serializers


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    workflow_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        read_only_fields = ('created', 'updated')
