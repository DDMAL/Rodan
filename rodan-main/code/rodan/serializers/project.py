from rodan.models.project import Project
from rodan.models.workflow import Workflow
from rodan.models.resource import Resource
from rest_framework import serializers
from rodan.serializers import AbsoluteURLField


class ProjectWorkflowSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Workflow
        fields = ("url", "name")


class ProjectResourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Resource
        fields = ("url", "name")


class ProjectListSerializer(serializers.HyperlinkedModelSerializer):
    workflow_count = serializers.IntegerField(read_only=True)
    resource_count = serializers.IntegerField(read_only=True)
    resourcelist_count = serializers.IntegerField(read_only=True)
    creator = serializers.SlugRelatedField(slug_field="username", read_only=True)
    admins = serializers.SerializerMethodField()
    workers = serializers.SerializerMethodField()

    def get_admins(self, obj):
        return obj.admin_group.user_set.values_list("username", flat=True)

    def get_workers(self, obj):
        return obj.worker_group.user_set.values_list("username", flat=True)

    class Meta:
        model = Project
        fields = (
            "url",
            "uuid",
            "name",
            "description",
            "creator",
            "admins",
            "workers",
            "created",
            "updated",
            "workflow_count",
            "resource_count",
            "resourcelist_count",
            "admins",
            "workers",
        )
        read_only_fields = ("created", "updated", "creator")


class ProjectDetailSerializer(serializers.HyperlinkedModelSerializer):
    workflows = ProjectWorkflowSerializer(many=True, read_only=True)
    resources = ProjectResourceSerializer(many=True, read_only=True)
    resourcelists = ProjectResourceSerializer(many=True, read_only=True)
    creator = serializers.SlugRelatedField(slug_field="username", read_only=True)
    admins = serializers.SerializerMethodField()
    workers = serializers.SerializerMethodField()
    admins_url = AbsoluteURLField(source="admins_relurl", read_only=True)
    workers_url = AbsoluteURLField(source="workers_relurl", read_only=True)

    def get_admins(self, obj):
        return obj.admin_group.user_set.values_list("username", flat=True)

    def get_workers(self, obj):
        return obj.worker_group.user_set.values_list("username", flat=True)

    class Meta:
        model = Project
        fields = (
            "url",
            "name",
            "description",
            "creator",
            "workflows",
            "resources",
            "resourcelists",
            "created",
            "updated",
            "admins",
            "workers",
            "admins_url",
            "workers_url",
        )

        read_only_fields = ("created", "updated")
