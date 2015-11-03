from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rodan.models.workflowjob import WorkflowJob
from rodan.serializers.workflowjob import WorkflowJobSerializer
from rodan.permissions import CustomObjectPermissions
from rest_framework import filters
from rodan.exceptions import CustomAPIException

class WorkflowJobList(generics.ListCreateAPIView):
    """
    Returns a list of all WorkflowJobs. Accepts a POST request with a data body
    to create a new WorkflowJob. POST requests will return the newly-created
    WorkflowJob object.
    """
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions, )
    _ignore_model_permissions = True
    queryset = WorkflowJob.objects.all()
    serializer_class = WorkflowJobSerializer
    filter_fields = {
        "updated": ['lt', 'gt'],
        "group": ['exact'],
        "uuid": ['exact'],
        "workflow": ['exact'],
        "created": ['lt', 'gt'],
        "job": ['exact'],
        "name": ['exact', 'icontains']
    }

    def perform_create(self, serializer):
        if not 'job_settings' in serializer.validated_data:
            j_settings = serializer.validated_data['job'].settings
            s = {}
            for properti, definition in j_settings.get('properties', {}).iteritems():
                if 'default' in definition:
                    s[properti] = definition['default']
            serializer.validated_data['job_settings'] = s
        serializer.save()


class WorkflowJobDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Performs operations on a single WorkflowJob instance.
    """
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions, )
    _ignore_model_permissions = True
    queryset = WorkflowJob.objects.all()
    serializer_class = WorkflowJobSerializer

    def perform_update(self, wfj_serializer):
        if wfj_serializer.instance.group is not None:
            # only allow job_settings to be updated
            invalid_info = {}
            for k, v in wfj_serializer.validated_data.iteritems():
                if k != 'job_settings':
                    invalid_info[k] = "To modify this field, you should first remove it from the group."
            if invalid_info:
                raise CustomAPIException(invalid_info, status=status.HTTP_400_BAD_REQUEST)
        wfj_serializer.save()

    def perform_destroy(self, wfj):
        if wfj.group is not None:
            raise CustomAPIException("To delete this workflowjob, you should first remove it from the group.", status=status.HTTP_400_BAD_REQUEST)
        wfj.delete()
