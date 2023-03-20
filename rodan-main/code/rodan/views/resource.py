import datetime
# import mimetypes
import os
import re
# import urlparse
import six.moves.urllib.parse

from celery import registry
from django.conf import settings
from django.core.urlresolvers import (
    reverse,
    resolve,
    Resolver404,
)
from django.db.models import ProtectedError
from django.db.models import Q
from django.db.utils import DataError
from django.http import (
    Http404,
    FileResponse
    # HttpResponseRedirect
)
from django.shortcuts import render
from django.utils import timezone
import django_filters
from rest_framework import (
    status,
    generics,
    permissions,
)
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from rodan.constants import task_status
from rodan.models import (
    Resource,
    ResourceLabel,
    ResourceType,
    Tempauthtoken,
)
from rodan.serializers.resourcetype import ResourceTypeSerializer
from rodan.serializers.resource import ResourceSerializer
from rodan.serializers.resourcelabel import ResourceLabelSerializer
from rodan.permissions import CustomObjectPermissions
from rodan.exceptions import CustomAPIException


class ResourceList(generics.ListCreateAPIView):
    """
    Returns a list of Resources. Accepts a POST request with a data body with
    multiple files to create new Resource objects. It will return the newly
    created Resource objects.

    **Parameters**

    - `result_of_workflow_run` -- GET-only. UUID of a WorkflowRun. Filters the results
      of a WorkflowRun.
    - `type` -- (optional) POST-only. User can claim the type of the files using
       this parameter to help Rodan convert it into compatible format. It could be:
        - An arbitrary MIME-type string.
        - Or a hyperlink to a ResourceType object.
    - `files` -- POST-only. The files.
    """
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    _ignore_model_permissions = True
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

    class filter_class(django_filters.FilterSet):
        # https://github.com/alex/django-filter/issues/273
        origin__isnull = django_filters.BooleanFilter(
            # action=lambda q, v: q.filter(origin__isnull=v)
            method=lambda q, v: q.filter(origin__isnull=v)
        )

        # resource_type__in = django_filters.MethodFilter()

        # def filter_resource_type__in(self, q, v):
        #     vs = v.split(',')
        #     return q.filter(resource_type__uuid__in=vs)

        resource_type__in = django_filters.filters.CharFilter(method="filter_resource_type__in")

        labels = django_filters.ModelMultipleChoiceFilter(
            field_name="labels",
            conjoined=True,
            queryset=ResourceLabel.objects.all()
        )

        def filter_resource_type__in(self, qs, name, value):
            value = value.split(",")
            return qs.filter(**{name: value})

        class Meta:
            model = Resource
            fields = {
                "origin": ['exact'],
                "updated": ['lt', 'gt'],
                "uuid": ['exact'],
                "creator": ['exact'],
                "creator__username": ['icontains'],
                # "has_thumb": ['exact'],
                "processing_status": ['exact'],
                "created": ['lt', 'gt'],
                "project": ['exact'],
                "resource_type": ['exact'],
                "name": ['exact', 'icontains'],
            }

    def get_queryset(self):
        # [TODO] filter according to the user?
        condition = Q()  # "ground" value of Q

        wfrun_uuid = self.request.query_params.get('result_of_workflow_run', None)
        if wfrun_uuid:
            condition &= Q(origin__run_job__workflow_run__uuid=wfrun_uuid) & (Q(inputs__isnull=True) | ~Q(inputs__run_job__workflow_run__uuid=wfrun_uuid) | Q(inputs__run_job__job_name="Labeler")) # noqa

        uploaded = self.request.query_params.get('uploaded', None)
        if uploaded == u'True':
            condition &= Q(origin__isnull=True)
        elif uploaded == u'False':
            condition &= Q(origin__isnull=False)

        # finding the resourcelist query parameter and adding it to the condition
        resource_list_param = self.request.query_params.get('resource_list', None)
        if resource_list_param is not None:
            resource_list_param = re.search(
                r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',
                resource_list_param
            )
            if resource_list_param is not None:
                resource_list_param = resource_list_param.group()
            from rodan.models import ResourceList
            resource_list = ResourceList.objects.filter(uuid=resource_list_param)
            if resource_list.exists():
                resource_list = ResourceList.objects.get(uuid=resource_list_param)
                resources = resource_list.resources
                resource_list_condition = Q()
                for r in resources.all():
                    resource_list_condition |= Q(uuid=r.uuid)
            else:
                # if the resource_list was not found, returns empty list
                resource_list_condition = Q(uuid=None)
            condition &= resource_list_condition

        # then this queryset is filtered on `filter_fields`
        queryset = Resource.objects.filter(condition)
        return queryset

    def paginate_queryset(self, queryset, view=None):
        if 'no_page' in self.request.query_params:
            return None
        else:
            return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def post(self, request, *args, **kwargs):
        if not request.data.get('files', None):
            raise ValidationError({'files': ["You must supply at least one file to upload."]})
        if not request.data.get('project', None):
            raise ValidationError({'project': ["This field is required."]})

        claimed_mimetype = request.data.get('type', None)
        if claimed_mimetype:
            try:
                # try to see if user provide a url to ResourceType
                # convert to relative url
                path = six.moves.urllib.parse.urlparse(claimed_mimetype).path
                match = resolve(path)                            # find a url route
                restype_pk = match.kwargs.get('pk')              # extract pk
                restype_obj = ResourceType.objects.get(pk=restype_pk)   # find object
                claimed_mimetype = restype_obj.mimetype          # find mimetype name
            except (Resolver404, ResourceType.DoesNotExist) as e:
                print(str(e))

        submitted_label_names = request.data.get('label_names', None)
        label_urls = []
        if submitted_label_names is not None:
            label_names = filter(lambda x: len(x) > 0, submitted_label_names.split(','))
            for name in label_names:
                try:
                    resource_label, _ = ResourceLabel.objects.get_or_create(name=name)
                    label_urls.append(
                        ResourceLabelSerializer(
                            resource_label,
                            context={'request': request}
                        ).data['url']
                    )
                except DataError:
                    # If the label specified is too long
                    continue

        initial_data = {
            'labels': label_urls,
            'resource_type': ResourceTypeSerializer(
                ResourceType.objects.get(mimetype='application/octet-stream'),
                context={'request': request}).data['url'],
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

            # arbitrarily provide one as Django will figure out the path according to upload_to
            resource_obj.resource_file.save(fileobj.name, fileobj)

            resource_id = str(resource_obj.uuid)
            mimetype = claimed_mimetype or "application/octet-stream"
            registry.tasks['rodan.core.create_resource'].si(resource_id, mimetype).apply_async()

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

    def patch(self, request, *args, **kwargs):
        resource_type = request.data.get('resource_type', None)
        resource = self.get_object()
        if resource_type:
            try:
                # try to see if user provide a url to ResourceType
                # convert to relative url
                path = six.moves.urllib.parse.urlparse(resource_type).path
                match = resolve(path)                            # find a url route
                restype_pk = match.kwargs.get('pk')              # extract pk
                restype_obj = ResourceType.objects.get(pk=restype_pk)   # find object
                claimed_mimetype = restype_obj.mimetype          # find mimetype name
            except (Resolver404, ResourceType.DoesNotExist) as e:
                print(str(e))
            if claimed_mimetype.startswith('image'):
                registry.tasks['rodan.core.create_diva'].si(resource.uuid).apply_async()

        resource_label_names = request.data.get('label_names', None)
        if resource_label_names is not None:
            label_objs = []
            label_names = filter(lambda x: len(x) > 0, resource_label_names.split(','))
            for name in label_names:
                try:
                    resource_label, _ = ResourceLabel.objects.get_or_create(name=name)
                    label_objs.append(resource_label)
                except DataError:
                    # This will happen if the label is too long.
                    continue

            # Update labels in many-to-many field
            current_labels = resource.labels.all()
            labels_to_add = [label for label in label_objs if label not in current_labels]
            labels_to_remove = [label for label in current_labels if label not in label_objs]
            for label in labels_to_add:
                resource.labels.add(label)
            for label in labels_to_remove:
                resource.labels.remove(label)
                if label.resource_set.count() == 0:
                    label.delete()

        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):

        resource = self.get_object()
        old_data = ResourceSerializer(resource, context={'request': request}).data

        try:
            resource.delete()
        except ProtectedError:
            return Response(
                {
                    "Error":
                        (
                            "You can not delete the resource because it is currently Protected. "
                            "A finished or pending runjob is referencing this resource. "
                            "If you delete that runjob, you can then delete this resource."
                        ),
                },
                status=status.HTTP_409_CONFLICT
            )

        return Response(old_data, status=status.HTTP_204_NO_CONTENT)


class ResourceViewer(APIView):
    """
    Get a viewer of the resource. If there is no viewer, redirect to resource file.

    Currently supports:
    + Diva.js: for all images (if jp2 and measurement json exist)
    + Neon.js: for MEI
    """
    # permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions, )
    _ignore_model_permissions = True
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

    # authentication_classes = ()
    permission_classes = (permissions.AllowAny, )

    def get(self, request, resource_uuid, working_user_token, *a, **k):
        # check expiry
        working_user_expiry = Tempauthtoken.objects.get(uuid=working_user_token).expiry
        if timezone.now() > working_user_expiry:
            raise CustomAPIException(
                {'message': 'Permission denied'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        resource = Resource.objects.get(uuid=resource_uuid)
        viewer = resource.get_viewer()
        if viewer == 'diva':
            return render(
                request,
                'diva.html',
                {
                    'page_title': "View Resource: {0}".format(resource.name or resource.pk),
                    'diva_object_data': resource.diva_json_url,
                    'diva_iip_server': settings.IIPSRV_URL,
                    'diva_image_dir': resource.diva_image_dir
                },
                content_type="text/html"
            )
        elif viewer == 'neon':
            return render(request, 'neon_square_viewer.html', {
                'mei_name': resource.name or resource.pk,
                'mei_url': resource.resource_url
            }, content_type="text/html")
        else:
            raise Http404("No viewer for this Resource.")


class ResourceAcquireView(generics.GenericAPIView):
    """
    Acquire a viewer url
    """
    lookup_url_kwarg = "resource_uuid"  # for self.get_object()
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions, )
    _ignore_model_permissions = True
    queryset = Resource.objects.all()

    def get_serializer_class(self):

        # for rest browsable API displaying the PUT/PATCH form
        from rest_framework import serializers

        class DummySerializer(serializers.Serializer):
            pass  # empty class

        return DummySerializer

    def post(self, request, resource_uuid, *args, **kwargs):
        expiry_date = timezone.now() + datetime.timedelta(
            seconds=settings.RODAN_RUNJOB_WORKING_USER_EXPIRY_SECONDS
        )
        user = request.user

        # remove the existing token to produce a new one
        if len(Tempauthtoken.objects.filter(user=user)) > 0:
            temp_token = Tempauthtoken.objects.get(user=request.user)
            temp_token.delete()

        temp_token = Tempauthtoken(user=user, expiry=expiry_date)
        temp_token.save()

        working_user_token = temp_token.uuid

        return Response({
            'working_url': request.build_absolute_uri(
                reverse(
                    'resource-viewer',
                    kwargs={
                        'resource_uuid': str(resource_uuid),
                        'working_user_token': str(working_user_token)
                    }
                )
            ),
            'working_user_expiry': expiry_date
        })


class ResourceArchive(generics.GenericAPIView):
    """
    Create and return an archive of resource files
    """

    permission_classes = (permissions.IsAuthenticated,)
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

    def get(self, request, format=None):
        resource_uuids = request.query_params.getlist('resource_uuid', None)
        if not resource_uuids:
            raise ValidationError({'resource_uuid': ["You must supply a list of resource UUIDs."]})

        archive = registry.tasks['rodan.core.create_archive'] \
            .si(resource_uuids).apply_async(queue="celery")
        storage = archive.get()
        if storage is None:
            raise ValidationError({'resource_uuid': ["The specified resources must exist."]})
        response = FileResponse(
            storage,
            content_type="application/zip"
        )
        response['Content-Disposition'] = "attachment; filename=Archive.zip"
        return response
