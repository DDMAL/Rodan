from rodan.models.workflow import Workflow
from rest_framework import serializers

from rodan.serializers.workflowjob import WorkflowJobSerializer
from rodan.serializers.job import JobSerializer
from rodan.serializers.page import PageSerializer


class WorkflowSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.HyperlinkedRelatedField(view_name="project-detail")
    # pages = serializers.ManyHyperlinkedRelatedField(view_name="page-detail", null=True)
    pages = PageSerializer()
    # jobs = JobSerializer()

    wjobs = WorkflowJobSerializer()

    uuid = serializers.Field(source='uuid')

    class Meta:
        model = Workflow
        read_only_fields = ('created', 'updated')
        fields = ("url",
                  "uuid",
                  "name",
                  "project",
                  'wjobs',
                  # "jobs",
                  'run',
                  "pages",
                  "description",
                  "has_started",
                  "created",
                  "updated")
