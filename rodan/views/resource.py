import mimetypes
from celery import registry
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from django.core.urlresolvers import Resolver404
from rodan.helpers.object_resolving import resolve_to_object
from rodan.models import RunJob, Project, Output, Resource, ResourceType
from rodan.models.resource import ResourceProcessingStatus
from rodan.serializers.resource import ResourceSerializer
from rodan.jobs.helpers import ensure_compatible, create_thumbnails
from django.db.models import Q

#class ResourceFilter(django_filters.FilterSet):


class ResourceList(generics.ListCreateAPIView):
    """
    Returns a list of Resources. Accepts a POST request with a data body with
    multiple files to create new Resource objects. It will return the newly
    created Resource objects.

    #### Parameters
    - `project` -- GET & POST. UUID of a Project.
    - `result_of_workflow_run` -- GET-only. UUID of a WorkflowRun. Filters the results
      of a WorkflowRun.
    - `origin` -- (optional) POST-only. UUID of an Output.
    - `type` -- (optional) POST-only. User can claim the type of the files using
       this parameter to help Rodan convert it into compatible format. It could be:
        - An arbitrary MIME-type string.
        - Or a hyperlink to a ResourceType object.
    - `files` -- POST-only. The files.
    """
    model = Resource
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ResourceSerializer
    filter_fields = ('project', )

    def get_queryset(self):
        # initial queryset (before filtering on `filter_fields`)
        queryset = Resource.objects.all()
        wfrun_uuid = self.request.QUERY_PARAMS.get('result_of_workflow_run', None)
        if wfrun_uuid:
            queryset = queryset.filter(Q(origin__run_job__workflow_run__uuid=wfrun_uuid) &
                                       (Q(inputs__isnull=True) | ~Q(inputs__run_job__workflow_run__uuid=wfrun_uuid)))
        return queryset

    def post(self, request, *args, **kwargs):
        if not request.FILES:
            return Response({'message': "You must supply at least one file to upload"}, status=status.HTTP_400_BAD_REQUEST)

        response = []
        current_user = User.objects.get(pk=request.user.id)

        project = request.DATA.get('project', None)
        if not project:
            return Response({'message': "You must supply project identifier for these resources."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project_obj = resolve_to_object(project, Project)
        except Resolver404:
            return Response({'message': "Could not resolve Project ID to a Project"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Project.DoesNotExist:
            return Response({'message': "No project with specified uuid exists"}, status=status.HTTP_400_BAD_REQUEST)

        origin = request.DATA.get('origin', None)
        if origin:
            try:
                output_obj = resolve_to_object(origin, Output)
            except Resolver404:
                return Response({'message': "Couldn't resolve specified output to an Output object"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Output.DoesNotExist:
                return Response({'message': "No runjob with specified uuid exists"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            output_obj = None

        claimed_mimetype = request.DATA.get('type', None)
        if claimed_mimetype:
            try:
                restype_obj = resolve_to_object(claimed_mimetype, ResourceType)
                claimed_mimetype = restype_obj.mimetype
            except (Resolver404, ResourceType.DoesNotExist):
                pass

        for fileobj in request.FILES.getlist('files'):
            resource_obj = Resource(name=fileobj.name,
                                    project=project_obj,
                                    creator=current_user,
                                    origin=output_obj,
                                    processing_status=ResourceProcessingStatus.WAITING,
                                    resource_type=ResourceType.cached('application/octet-stream'))
            resource_obj.save()
            resource_obj.resource_file.save(fileobj.name, fileobj)  # arbitrarily provide one as Django will figure out the path according to upload_to

            resource_id = str(resource_obj.uuid)
            mimetype = claimed_mimetype or mimetypes.guess_type(fileobj.name, strict=False)[0]
            (registry.tasks[ensure_compatible.name].si(resource_id, mimetype) | create_thumbnails.si(resource_id)).apply_async()

            try:
                d = ResourceSerializer(resource_obj, context={'request': request}).data
                response.append(d)
            except:
                return Response({'message': " Could not serialize resource object"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'resources': response}, status=status.HTTP_201_CREATED)


class ResourceDetail(generics.RetrieveUpdateAPIView):
    """
    Perform operations on a single Resource instance.
    """
    model = Resource
    serializer_class = ResourceSerializer
    permission_classes = (permissions.IsAuthenticated, )
