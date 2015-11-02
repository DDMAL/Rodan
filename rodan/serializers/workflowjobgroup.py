from rodan.models import WorkflowJobGroup

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
        if len(wfjs) > 0:
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
