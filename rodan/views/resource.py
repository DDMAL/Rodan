from django.contrib.auth.models import User
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from django.core.urlresolvers import Resolver404
from rodan.helpers.object_resolving import resolve_to_object
from rodan.models import RunJob, Project, Output, Resource, ResourceType
from rodan.models.resource import upload_path
from rodan.serializers.resource import ResourceSerializer
from rodan.jobs.helpers import ensure_compatible, create_thumbnails


class ResourceList(generics.ListCreateAPIView):
    """
    ## GET

    Retrieve all resources.

    - Supported query parameters:
        - `project=$ID`: filter resources belonging to project $ID.

    ## POST

    Create new resources.

    Accepts a POST request with a data body with multiple files to create new resource objects. It will return the newly created resource objects.

    - Supported query parameters:
        - `project=$ID`
        - `run_job=$ID`
        - `origin=$ID`
        - `type=string` File type, could be 'image'...
    """
    model = Resource
    paginate_by = None
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ResourceSerializer

    def get_queryset(self):
        queryset = Resource.objects.all()
        project = self.request.QUERY_PARAMS.get('project', None)

        if project:
            queryset = queryset.filter(project__uuid=project)

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

        run_job = request.DATA.get('run_job', None)
        if run_job:
            try:
                runjob_obj = resolve_to_object(run_job, RunJob)
            except Resolver404:
                return Response({'message': "Couldn't resolve specified RunJob to a RunJob object"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except RunJob.DoesNotExist:
                return Response({'message': "No runjob with specified uuid exists"}, status=status.HTTP_400_BAD_REQUEST)

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

        res_type = request.DATA.get('type', None)
        if not res_type:
            return Response({'message': "You must supply type for these resources."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                restype_obj = resolve_to_object(res_type, ResourceType)
            except Resolver404:
                return Response({'message': "Couldn't resolve specified resource type to a ResourceType object"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except ResourceType.DoesNotExist:
                return Response({'message': "Requested resource type does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        for fileobj in request.FILES.getlist('files'):
            resource_obj = Resource(name=fileobj.name,
                                    project=project_obj,
                                    creator=current_user,
                                    origin=output_obj,
                                    resource_type=ResourceType.cached('application/octet-stream'))
            resource_obj.save()
            resource_obj.resource_file.save(upload_path(resource_obj, fileobj.name), fileobj)

            resource_id = str(resource_obj.uuid)
            (ensure_compatible.si(resource_id, restype_obj.mimetype) | create_thumbnails.si(resource_id)).apply_async()

            try:
                d = ResourceSerializer(resource_obj, context={'request': request}).data
                response.append(d)
            except:
                return Response({'message': " Could not serialize resource object"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'resources': response}, status=status.HTTP_201_CREATED)


class ResourceDetail(generics.RetrieveUpdateAPIView):
    """
    Perform operations on a single resource instance.
    """
    model = Resource
    serializer_class = ResourceSerializer
    permission_classes = (permissions.IsAuthenticated, )
