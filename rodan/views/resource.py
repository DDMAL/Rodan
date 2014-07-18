import urlparse
import celery

from django.contrib.auth.models import User
from django.core.urlresolvers import resolve

from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response

from rodan.models.runjob import RunJob
from rodan.models.project import Project
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

        start_seq = int(request.DATA.get('resource_order', None))

        if not start_seq:
            return Response({'message': "The start sequence for the page ordering may not be empty."}, status=status.HTTP_400_BAD_REQUEST)

        project = request.DATA.get('project', None)
        if not project:
            return Response({'message': "You must supply project identifier for these resources."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project_obj = self._resolve_to_object(project, Project)
        except:
            return Response({'message': "Could not resolve Project ID to a Project"}, status=status.HTTP_400_BAD_REQUEST)

        run_job = request.DATA.get('run_job', None)
        if run_job:
            try:
                runjob_obj = self._resolve_to_object(run_job, RunJob)
            except:
                return Response({'message': "couldn't resolve runjob object tough luck buster"}, status=status.HTTP_400_BAD_REQUEST)

        for seq, fileobj in enumerate(request.FILES.getlist('files'), start=start_seq):
            resource_obj = Resource(name=fileobj.name,
                                    project=project_obj,
                                    resource_order=seq,
                                    resource_type=fileobj.content_type,
                                    creator=current_user)
            resource_obj.save()
            resource_obj.resource_file.save(upload_path(resource_obj, fileobj.name), fileobj)

            if runjob_obj:
                resource_obj.run_job = runjob_obj
                resource_obj.save()

            res = celery.chain(ensure_compatible.s(resource_obj), create_thumbnails.s(), processed.s())
            res.apply_async()

            try:
                d = ResourceSerializer(resource_obj).data
                response.append(d)
            except:
                return Response({'message': " Could not serialize resource object"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'resources': response}, status=status.HTTP_201_CREATED)

    def _resolve_to_object(self, request_url, model):
        value = urlparse.urlparse(request_url).path
        o = resolve(value)
        obj_pk = o.kwargs.get('pk')
        return model.objects.get(pk=obj_pk)


class ResourceDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Resource
    serializer_class = ResourceSerializer
    permission_classes = (permissions.IsAuthenticated, )
