import celery
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from django.core.urlresolvers import Resolver404
from rodan.helpers.object_resolving import resolve_to_object
from rodan.models.runjob import RunJob
from rodan.models.project import Project
from rodan.models.output import Output
from rodan.models.resource import Resource, upload_path
from rodan.serializers.resource import ResourceSerializer
from rodan.helpers.convert import ensure_compatible
from rodan.helpers.thumbnails import create_thumbnails
from rodan.helpers.processed import processed


class ResourceList(generics.ListCreateAPIView):
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

        for fileobj in request.FILES.getlist('files'):
            resource_obj = Resource(name=fileobj.name,
                                    project=project_obj,
                                    creator=current_user,
                                    origin=output_obj)
            resource_obj.save()
            resource_obj.resource_file.save(upload_path(resource_obj, fileobj.name), fileobj)

            if run_job:
                resource_obj.run_job = runjob_obj
                resource_obj.save()

            type = resource_obj.resource_type[0].split('/')[0]
            if type == 'image':
                res = celery.chain(ensure_compatible.s(resource_obj), create_thumbnails.s(), processed.s())
                res.apply_async()

            try:
                d = ResourceSerializer(resource_obj).data
                response.append(d)
            except:
                return Response({'message': " Could not serialize resource object"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'resources': response}, status=status.HTTP_201_CREATED)


class ResourceDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Resource
    serializer_class = ResourceSerializer
    permission_classes = (permissions.IsAuthenticated, )
