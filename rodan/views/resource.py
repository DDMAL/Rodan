import mimetypes, os, urlparse
from celery import registry
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.core.urlresolvers import Resolver404, resolve
from rodan.models import Project, Output, Resource, ResourceType
from rodan.serializers.resourcetype import ResourceTypeSerializer
from rodan.serializers.resource import ResourceSerializer
from django.db.models import Q
from rodan.constants import task_status
from django.http import Http404, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render
import django_filters
from rodan.permissions import CustomObjectPermissions
from rest_framework import filters

class ResourceList(generics.ListCreateAPIView):
    """
    Returns a list of Resources. Accepts a POST request with a data body with
    multiple files to create new Resource objects. It will return the newly
    created Resource objects.

    #### Other Parameters
    - `result_of_workflow_run` -- GET-only. UUID of a WorkflowRun. Filters the results
      of a WorkflowRun.
    - `type` -- (optional) POST-only. User can claim the type of the files using
       this parameter to help Rodan convert it into compatible format. It could be:
        - An arbitrary MIME-type string.
        - Or a hyperlink to a ResourceType object.
    - `files` -- POST-only. The files.
    """
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions, )
    _ignore_model_permissions = True
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

    class filter_class(django_filters.FilterSet):
        origin__isnull = django_filters.BooleanFilter(action=lambda q, v: q.filter(origin__isnull=v))  # https://github.com/alex/django-filter/issues/273
        resource_type__in = django_filters.MethodFilter()

        def filter_resource_type__in(self, q, v):
            vs = v.split(',')
            return q.filter(resource_type__uuid__in=vs)

        class Meta:
            model = Resource
            fields = {
                "origin": ['exact'],
                "updated": ['lt', 'gt'],
                "uuid": ['exact'],
                "creator": ['exact'],
                "has_thumb": ['exact'],
                "processing_status": ['exact'],
                "created": ['lt', 'gt'],
                "project": ['exact'],
                "resource_type": ['exact'],
                "name": ['exact', 'icontains']
            }

    def get_queryset(self):
        # [TODO] filter according to the user?
        condition = Q()  # "ground" value of Q

        wfrun_uuid = self.request.query_params.get('result_of_workflow_run', None)
        if wfrun_uuid:
            condition &= Q(origin__run_job__workflow_run__uuid=wfrun_uuid) & (Q(inputs__isnull=True) | ~Q(inputs__run_job__workflow_run__uuid=wfrun_uuid))

        uploaded = self.request.query_params.get('uploaded', None)
        if uploaded == u'True':
            condition &= Q(origin__isnull=True)
        elif uploaded == u'False':
            condition &= Q(origin__isnull=False)

        queryset = Resource.objects.filter(condition)  # then this queryset is filtered on `filter_fields`
        return queryset

    def post(self, request, *args, **kwargs):
        if not request.data.get('files', None):
            raise ValidationError({'files': ["You must supply at least one file to upload."]})
        claimed_mimetype = request.data.get('type', None)
        if claimed_mimetype:
            try:
                # try to see if user provide a url to ResourceType
                path = urlparse.urlparse(claimed_mimetype).path  # convert to relative url
                match = resolve(path)                            # find a url route
                restype_pk = match.kwargs.get('pk')              # extract pk
                restype_obj = ResourceType.objects.get(pk=restype_pk)   # find object
                claimed_mimetype = restype_obj.mimetype          # find mimetype name
            except (Resolver404, ResourceType.DoesNotExist) as e:
                print str(e)


        initial_data = {
            'resource_type': ResourceTypeSerializer(ResourceType.objects.get(mimetype='application/octet-stream'), context={'request': request}).data['url'],
            'processing_status': task_status.SCHEDULED
        }
        if 'project' in request.data:
            initial_data['project'] = request.data['project']

        new_resources = []
        for fileobj in request.data.getlist('files'):
            serializer = ResourceSerializer(data=initial_data, context={'request': request})
            serializer.is_valid(raise_exception=True)

            filename_without_ext = os.path.splitext(fileobj.name)[0]
            resource_obj = serializer.save(name=filename_without_ext, creator=request.user)
            resource_obj.resource_file.save(fileobj.name, fileobj)  # arbitrarily provide one as Django will figure out the path according to upload_to

            resource_id = str(resource_obj.uuid)
            mimetype = claimed_mimetype or mimetypes.guess_type(fileobj.name, strict=False)[0]
            registry.tasks['rodan.core.ensure_compatible'].si(resource_id, mimetype).apply_async()

            d = ResourceSerializer(resource_obj, context={'request': request}).data
            new_resources.append(d)

        return Response(new_resources, status=status.HTTP_201_CREATED)


class ResourceDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Perform operations on a single Resource instance.
    """
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions, )
    _ignore_model_permissions = True
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

class ResourceViewer(generics.RetrieveAPIView):
    """
    Get a viewer of the resource. If there is no viewer, redirect to compat resource file.

    Currently supports:
    + Diva.js: for all images (if jp2 and measurement json exist)
    + Neon.js: for MEI
    """
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions, )
    _ignore_model_permissions = True
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

    def get(self, request, *a, **k):
        resource = self.get_object()
        viewer = resource.get_viewer()
        if viewer == 'diva':
            return render(request, 'diva.html', {
                'page_title': "View Resource: {0}".format(resource.name or resource.pk),
                'diva_object_data': resource.diva_json_url,
                'diva_iip_server': settings.IIPSRV_URL,
                'diva_image_dir': resource.diva_image_dir
            }, content_type="text/html")
        elif viewer == 'neon':
            return render(request, 'neon_square_viewer.html', {
                'mei_name': resource.name or resource.pk,
                'mei_url': resource.compat_file_url
            }, content_type="text/html")
        else:
            raise Http404("No viewer for this Resource.")
