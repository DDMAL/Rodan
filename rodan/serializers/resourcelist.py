from rodan.models import ResourceList
from rest_framework import serializers


class ResourceListSerializer(serializers.HyperlinkedModelSerializer):
    creator = serializers.SlugRelatedField(slug_field="username", read_only=True)
    class Meta:
        model = ResourceList
        read_only_fields = ('created', 'updated', 'resource_type', 'origin', 'creator')
        fields = ('url', 'uuid', 'name', 'description', 'project', 'resources', 'resource_type', 'origin', 'created', 'updated', 'creator')

    def validate_resources(self, resources):
        if resources is not None and len(resources) > 0:
            first_p = resources[0].project
            first_rt = resources[0].resource_type
            for r in resources[1:]:
                if r.project != first_p:
                    raise serializers.ValidationError("All Resources should belong to the same Project.")
                if r.resource_type != first_rt:
                    raise serializers.ValidationError("All Resources should have the same ResourceType.")
        return resources

    def save(self, **kwargs):
        """
        Update `project` and `resource_type` fields in database.
        """
        resources = self.validated_data.get('resources')
        if resources is not None and len(resources) > 0:
            self.validated_data['project'] = self.validated_data['resources'][0].project
            self.validated_data['resource_type'] = self.validated_data['resources'][0].resource_type

        try:
            project = self.data.get('project')
            return super(ResourceListSerializer, self).save(**kwargs)
        except:
            try:
                project = self.validated_data['project']
                return super(ResourceListSerializer, self).save(**kwargs)
            except:
                raise serializers.ValidationError("Resource List should belong to a Project.")
