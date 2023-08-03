from rest_framework import serializers
from rodan.models.user import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    projects = serializers.HyperlinkedRelatedField(
        view_name="project-detail", many=True, read_only=True
    )
    workflows = serializers.HyperlinkedRelatedField(
        view_name="workflow-detail", many=True, read_only=True
    )
    workflow_runs = serializers.HyperlinkedRelatedField(
        view_name="workflowrun-detail", many=True, read_only=True
    )

    class Meta:
        model = User
        fields = (
            "url",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_active",
            "is_superuser",
            "projects",
            "workflows",
            "workflow_runs",
            "user_preference",
        )


class UserListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ("url", "username", "first_name", "last_name")
