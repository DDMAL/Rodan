import json, tempfile, inspect, os, mimetypes
from celery import registry
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, Http404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import permissions, generics
from rest_framework.exceptions import APIException
from rodan.models import RunJob
from rodan.constants import task_status
import time
import datetime
from django.utils import timezone
import uuid
from django.core.urlresolvers import reverse
from rodan.exceptions import CustomAPIException
from rodan.permissions import CustomObjectPermissions

RODAN_RUNJOB_WORKING_USER_EXPIRY_SECONDS = settings.RODAN_RUNJOB_WORKING_USER_EXPIRY_SECONDS

class InteractiveAcquireView(generics.GenericAPIView):
    """
    Acquire an interactive runjob.
    """
    lookup_url_kwarg = "run_job_uuid"  # for self.get_object()
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions, )
    _ignore_model_permissions = True
    queryset = RunJob.objects.all()
    def get_serializer_class(self):
        # for rest browsable API displaying the PUT/PATCH form
        from rest_framework import serializers
        class DummySerializer(serializers.Serializer):
            pass   # empty class
        return DummySerializer

    def post(self, request, run_job_uuid, *args, **kwargs):
        # check runjob
        runjob = self.get_object()
        if runjob.status != task_status.WAITING_FOR_INPUT:
            return Response({'message': 'This RunJob does not accept input now'}, status=status.HTTP_400_BAD_REQUEST)

        if runjob.working_user and request.user != runjob.working_user and timezone.now() <= runjob.working_user_expiry:
            # last working user not expired yet
            return Response({'message': 'Previous working user has not expired yet.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if request.user != runjob.working_user or timezone.now() > runjob.working_user_expiry:
                # reset working user as current user
                runjob.working_user = request.user
                runjob.working_user_token = uuid.uuid4()
            if runjob.working_user_token is None:
                runjob.working_user_token = uuid.uuid4()
            runjob.working_user_expiry = timezone.now() + datetime.timedelta(seconds=RODAN_RUNJOB_WORKING_USER_EXPIRY_SECONDS)  # extend expiry time
            runjob.save(update_fields=['working_user', 'working_user_token', 'working_user_expiry'])

            return Response({
                'working_url': request.build_absolute_uri(reverse('interactive-working', kwargs={'run_job_uuid': str(run_job_uuid), 'working_user_token': str(runjob.working_user_token), 'additional_url': ''})),
                'working_user_expiry': runjob.working_user_expiry
            })


class InteractiveWorkingView(APIView):
    """
    Rodan makes available interfaces for interactive jobs. Each endpoint accepts
    GET and POST requests.

    #### Parameters
    - `**kwargs` -- POST-only. Job settings.
    """
    authentication_classes = ()
    permission_classes = (permissions.AllowAny, )

    def _authenticate(self, run_job_uuid, working_user_token):
        # check runjob
        runjob = get_object_or_404(RunJob, uuid=run_job_uuid)
        if runjob.status != task_status.WAITING_FOR_INPUT:
            raise CustomAPIException({'message': 'This RunJob does not accept input now'}, status=status.HTTP_400_BAD_REQUEST)

        # check token
        if runjob.working_user_token != uuid.UUID(working_user_token):
            raise CustomAPIException({'message': 'Permission denied'}, status=status.HTTP_401_UNAUTHORIZED)

        # check expiry
        if timezone.now() > runjob.working_user_expiry:
            raise CustomAPIException({'message': 'Permission denied'}, status=status.HTTP_401_UNAUTHORIZED)

        return runjob

    def get(self, request, run_job_uuid, working_user_token, additional_url, *a, **k):
        runjob = self._authenticate(run_job_uuid, working_user_token)
        manual_task = registry.tasks[str(runjob.job_name)]

        if not additional_url:
            # request for the interface. Track the time
            template, context = manual_task.get_interface(run_job_uuid)

            c = RequestContext(request, context)
            response = HttpResponse(template.render(c))
            runjob.interactive_timings.append({'get': time.time()})
            runjob.save(update_fields=['interactive_timings'])
            return response
        else:
            # request for static files
            ## find the path of the static file. Need to figure out the package name
            job_package_path = manual_task._package_path()
            job_static_path = os.path.join(job_package_path, 'static')  # e.g.: "/path/to/rodan/jobs/gamera/static"
            if os.path.isabs(additional_url) or additional_url == '..' or additional_url.startswith('../'):  # prevent traversal (from flask https://github.com/mitsuhiko/flask/blob/master/flask/helpers.py#L567-L591)
                raise Http404
            abspath = os.path.join(job_static_path, additional_url)

            with open(abspath, 'rb') as fsock:
                mime_type = mimetypes.guess_type(abspath)[0]
                return HttpResponse(fsock, content_type=mime_type)

    def post(self, request, run_job_uuid, working_user_token, additional_url, *a, **k):
        runjob = self._authenticate(run_job_uuid, working_user_token)

        if isinstance(request.data, dict) and "__serialized__" in request.data:
            user_input = json.loads(request.data['__serialized__'])
        else:
            user_input = request.data

        manual_task = registry.tasks[str(runjob.job_name)]
        try:
            setattr(manual_task, 'url', additional_url)  # Set additional information on the object
            retval = manual_task.validate_user_input(run_job_uuid, user_input)
            del manual_task.url
        except APIException as e:
            raise e

        if isinstance(retval, manual_task.WAITING_FOR_INPUT):
            settings_update = retval.settings_update
            runjob.job_settings.update(settings_update)
            runjob.save()
            if retval.response:
                return HttpResponse(retval.response, status=status.HTTP_200_OK)
            
        elif 'manual' in retval:
            runjob.interactive_timings.append({'post': time.time()})
            return Response(retval, status = status.HTTP_200_OK)
            
        else:
            settings_update = retval
            runjob.status = task_status.SCHEDULED
            runjob.error_summary = ''
            runjob.error_details = ''
            runjob.job_settings.update(settings_update)
            runjob.interactive_timings.append({'post': time.time()})
            runjob.working_user = None
            runjob.working_user_token = None
            runjob.working_user_expiry = None
            runjob.save()
            # call master_task to continue workflowrun
            registry.tasks['rodan.core.master_task'].apply_async((runjob.workflow_run.uuid,))
        return Response(status=status.HTTP_200_OK)
