from django.contrib.auth.models import User
from rodan.models.project import Project
from rodan.models.workflow import Workflow
from rodan.models.resource import Resource
from rest_framework import serializers


class ProjectCreatorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username',)

class ProjectWorkflowSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Workflow

class ProjectResourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Resource

class ProjectListSerializer(serializers.HyperlinkedModelSerializer):
    workflow_count = serializers.IntegerField(read_only=True)
    resource_count = serializers.IntegerField(read_only=True)
    creator = ProjectCreatorSerializer(read_only=True)
    uuid = serializers.CharField(read_only=True)

    class Meta:
        model = Project
        read_only_fields = ('created', 'updated')


class ProjectDetailSerializer(serializers.HyperlinkedModelSerializer):
    workflow_count = serializers.IntegerField(read_only=True)
    resource_count = serializers.IntegerField(read_only=True)
    workflows = ProjectWorkflowSerializer(many=True, read_only=True)
    resources = ProjectResourceSerializer(many=True, read_only=True)
    creator = ProjectCreatorSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ('url',
                  'name',
                  'creator',
                  'workflow_count',
                  'resource_count',
                  'workflows',
                  'resources',
                  'created',
                  'updated')

        read_only_fields = ('created', 'updated')
