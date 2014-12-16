from rest_framework import serializers
from rodan.models import ResourceCollection

class ResourceCollectionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ResourceCollection
        fields = ("url",
                  "uuid",
                  "resources",
                  "workflow")

    def validate(self, data):
        if self.partial:
            wf = data.get('workflow', self.instance.workflow)
            resources = data.get('resources', self.instance.resources.all())
        else:
            wf = data['workflow']
            resources = data.get('resources', ())
        proj = wf.project

        for r in resources:
            if r.project != proj:
                raise serializers.ValidationError('Resource {0} is not in the same project as the Workflow'.format(r.uuid.hex))
        return data
