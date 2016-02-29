from rodan.models import ResourceList
from rest_framework import serializers


class ResourceListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ResourceList
        read_only_fields = ('created', 'updated', 'project', 'resource_type', 'origin')
        fields = ('url', 'uuid', 'name', 'description', 'project', 'resources', 'resource_type', 'origin', 'created', 'updated')

    def validate_resources(self, resources):
        if len(resources) == 0:
            raise serializers.ValidationError("This list may not be empty.")
        else:
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
        if self.validated_data.get('resources'):
            self.validated_data['project'] = self.validated_data['resources'][0].project
            self.validated_data['resource_type'] = self.validated_data['resources'][0].resource_type
            return super(ResourceListSerializer, self).save(**kwargs)
