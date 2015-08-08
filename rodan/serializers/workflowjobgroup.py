from rodan.models import WorkflowJobGroup

from rest_framework import serializers

class WorkflowJobGroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WorkflowJobGroup
        read_only_fields = ('created', 'updated', 'origin')
        fields = ("url",
                  "uuid",
                  "origin",
                  "workflow_jobs",
                  "created",
                  "updated")

    def validate_workflow_jobs(self, wfjs):
        if len(wfjs) > 0:
            first_wf_uuid = wfjs[0].uuid
            for wfj in wfjs[1:]:
                if wfj.uuid != first_wf_uuid:  # not in the same workflow
                    raise serializers.ValidationError("All WorkflowJobs should belong to the same Workflow.")

        return wfjs
