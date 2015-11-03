from rodan.models import WorkflowJobGroup

from rodan.serializers.workflow import version_map
from django.conf import settings
from rest_framework import serializers

class WorkflowJobGroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WorkflowJobGroup
        read_only_fields = ('created', 'updated', 'origin', 'workflow')
        fields = ("url",
                  "uuid",
                  "name",
                  "description",
                  "workflow",
                  "origin",
                  "workflow_jobs",
                  "created",
                  "updated")

    def validate_workflow_jobs(self, wfjs):
        if len(wfjs) == 0:
            raise serializers.ValidationError("Empty WorkflowJobGroup is not allowed.")
        else:
            first_wf = wfjs[0].workflow
            for wfj in wfjs[1:]:
                if wfj.workflow != first_wf:  # not in the same workflow
                    raise serializers.ValidationError("All WorkflowJobs should belong to the same Workflow.")

        return wfjs

    def save(self, **kwargs):
        """
        Update `workflow` field in database.
        """
        if self.validated_data.get('workflow_jobs'):
            self.validated_data['workflow'] = self.validated_data['workflow_jobs'][0].workflow
        return super(WorkflowJobGroupSerializer, self).save(**kwargs)


class WorkflowJobGroupImportCreateSerializer(serializers.HyperlinkedModelSerializer):
    """
    For importing workflow as workflowjobgroup. Check `workflow` and `origin` fields.
    """
    class Meta:
        model = WorkflowJobGroup
        read_only_fields = ('name', 'description', 'workflow_jobs', 'created', 'updated') # workflow and origin fields are not read-only.
        fields = ("url",
                  "uuid",
                  "name",
                  "description",
                  "workflow",
                  "origin",
                  "workflow_jobs",
                  "created",
                  "updated")

    def validate_origin(self, origin):
        if origin.valid is False:
            raise serializers.ValidationError("Origin workflow must be valid.")
        return origin

    def save(self, **kwargs):
        """
        Set up `name`, `description`, `workflow_jobs`, copy workflow jobs.
        """
        self.validated_data['name'] = "From Workflow {0}".format(self.validated_data['origin'].name[:80])
        self.validated_data['description'] = self.validated_data['origin'].description

        # dump origin workflow and load as a workflowjobgroup
        dumped_workflow = version_map[settings.RODAN_WORKFLOW_SERIALIZATION_FORMAT_VERSION].dump(self.validated_data['origin'])
        loaded_wfjs = version_map[settings.RODAN_WORKFLOW_SERIALIZATION_FORMAT_VERSION].load(dumped_workflow, self.validated_data['workflow'])

        self.validated_data['workflow_jobs'] = loaded_wfjs
        wfjgroup = super(WorkflowJobGroupImportCreateSerializer, self).save(**kwargs)
