from rodan.models import (
    ResourceList,
    # ResourceType,
    Project
)
from rest_framework import serializers
from rodan.serializers.resourcetype import ResourceTypeSerializer


# class ResourceTypeSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = ResourceType
#         fields = ("url", "mimetype")


class ResourceListSerializer(serializers.HyperlinkedModelSerializer):
    creator = serializers.SlugRelatedField(slug_field="username", read_only=True)
    resource_type = ResourceTypeSerializer(read_only=True)

    class Meta:
        model = ResourceList
        read_only_fields = ("created", "updated", "origin", "creator", "resource_type")
        fields = (
            "url",
            "uuid",
            "name",
            "description",
            "project",
            "resources",
            "resource_type",
            "origin",
            "created",
            "updated",
            "creator",
            "resource_type",
        )

    def validate_resources(self, resources):
        if resources is not None and len(resources) > 0:
            first_p = resources[0].project
            first_rt = resources[0].resource_type
            for r in resources[1:]:
                if r.project != first_p:
                    raise serializers.ValidationError(
                        "All Resources should belong to the same Project."
                    )
                if r.resource_type != first_rt:
                    raise serializers.ValidationError(
                        "All Resources should have the same ResourceType."
                    )
        return resources

    def save(self, **kwargs):
        """
        Update `project` and `resource_type` fields in database.
        """
        resources = self.validated_data.get("resources")

        project = self.validated_data.get("project")
        if project is None:
            # When project is not sent in the request (e.g. post, patch, ...)
            try:
                project_url = self.data.get("project")
                project_uuid = project_url.split("/")[-2]
                project = Project.objects.get(uuid=project_uuid)
            except AttributeError:
                raise serializers.ValidationError(
                    "Resource List should belong to a Project."
                )

        if resources is not None and len(resources) > 0:
            if project != self.validated_data["resources"][0].project:
                raise serializers.ValidationError(
                    "Resources should belong to the same Project as the Resource List."
                )
            self.validated_data["resource_type"] = self.validated_data["resources"][
                0
            ].resource_type

        return super(ResourceListSerializer, self).save(**kwargs)
