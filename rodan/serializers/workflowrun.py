from rodan.models.workflowrun import WorkflowRun
from rest_framework import serializers
from rodan.serializers import TransparentField

class WorkflowRunSerializer(serializers.HyperlinkedModelSerializer):
    uuid = serializers.CharField(read_only=True)
    origin_resources = TransparentField(read_only=True)
    creator = serializers.SlugRelatedField(slug_field="username", read_only=True)
    class Meta:
        model = WorkflowRun
        read_only_fields = ("created", "updated", 'creator', 'project')
        extra_kwargs = {
            'workflow': {'allow_null': False, 'required': True}
        }

class WorkflowRunByPageSerializer(serializers.HyperlinkedModelSerializer):
    uuid = serializers.CharField(read_only=True)
    origin_resources = TransparentField(read_only=True)
    creator = serializers.SlugRelatedField(slug_field="username", read_only=True)
    class Meta:
        model = WorkflowRun
        read_only_fields = ("created", "updated", 'creator', 'project')
        extra_kwargs = {
            'workflow': {'allow_null': False, 'required': True}
        }
