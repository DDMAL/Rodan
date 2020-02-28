from rodan.models.workflowrun import WorkflowRun
from rest_framework import serializers
from rodan.serializers import TransparentField


class WorkflowRunSerializer(serializers.HyperlinkedModelSerializer):
    uuid = serializers.CharField(read_only=True)
    origin_resources = TransparentField(read_only=True)
    creator = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = WorkflowRun
        read_only_fields = ("created", "updated", "creator", "project")
        fields = (
            "uuid",
            "project",
            "workflow",
            "creator",
            "status",
            "name",
            "description",
            "last_redone_runjob_tree",
            "created",
            "updated",
            "origin_resources",
            "creator",
        )
        extra_kwargs = {"workflow": {"allow_null": False, "required": True}}
        fields = "__all__"


class WorkflowRunByPageSerializer(serializers.HyperlinkedModelSerializer):
    uuid = serializers.CharField(read_only=True)
    origin_resources = TransparentField(read_only=True)
    creator = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = WorkflowRun
        read_only_fields = ("created", "updated", "creator", "project")
        fields = (
            "uuid",
            "project",
            "workflow",
            "creator",
            "status",
            "name",
            "description",
            "last_redone_runjob_tree",
            "created",
            "updated",
            "origin_resources",
            "creator",
        )
        extra_kwargs = {"workflow": {"allow_null": False, "required": True}}
