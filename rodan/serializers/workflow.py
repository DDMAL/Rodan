from rodan.models.workflow import Workflow
from rest_framework import serializers
from rodan.serializers.page import PageSerializer


class WorkflowSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.HyperlinkedRelatedField(view_name="project-detail")
    # pages = PageSerializer()
    pages = serializers.ManyHyperlinkedRelatedField(view_name="page-detail", null=True)
    jobs = serializers.ManyHyperlinkedRelatedField(view_name="job-detail", null=True)

    class Meta:
        model = Workflow
        read_only_fields = ('created', 'updated')
        fields = ("url",
                  "name",
                  "project",
                  "jobs",
                  "pages",
                  "description",
                  "has_started",
                  "created",
                  "updated")
