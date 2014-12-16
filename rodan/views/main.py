from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(('GET',))
@ensure_csrf_cookie
def api_root(request, format=None):
    """
    Browse all APIs of Rodan server.
    """
    response = {
        'routes': {'projects': reverse('project-list', request=request, format=format),
                     'workflows': reverse('workflow-list', request=request, format=format),
                     'workflowjobs': reverse('workflowjob-list', request=request, format=format),
                     'workflowruns': reverse('workflowrun-list', request=request, format=format),
                     'runjobs': reverse('runjob-list', request=request, format=format),
                     'jobs': reverse('job-list', request=request, format=format),
                     'users': reverse('user-list', request=request, format=format),
                     'resultspackages': reverse('resultspackage-list', request=request, format=format),
                     'connections': reverse('connection-list', request=request, format=format),
                     'resourceassignments': reverse('resourceassignment-list', request=request, format=format),
                     'resourcecollections': reverse('resourcecollection-list', request=request, format=format),
                     'outputporttypes': reverse('outputporttype-list', request=request, format=format),
                     'outputports': reverse('outputport-list', request=request, format=format),
                     'inputporttypes': reverse('inputporttype-list', request=request, format=format),
                     'inputports': reverse('inputport-list', request=request, format=format),
                     'resources': reverse('resource-list', request=request, format=format),
                     'resourcetypes': reverse('resourcetype-list', request=request, format=format),
                     'outputs': reverse('output-list', request=request, format=format),
                     'inputs': reverse('input-list', request=request, format=format),
                     'session-auth': reverse('session-auth', request=request, format=format),
                     'session-status': reverse('session-status', request=request, format=format),
                     'token-auth': reverse('token-auth', request=request, format=format),
                     'session-close': reverse('session-close', request=request, format=format),
                     'taskqueue-active': reverse('taskqueue-active', request=request, format=format),
                     'taskqueue-scheduled': reverse('taskqueue-scheduled', request=request, format=format),
                     'taskqueue-status': reverse('taskqueue-status', request=request, format=format),
                     'taskqueue-config': reverse('taskqueue-config', request=request, format=format)},
        'configuration': {
            'page_length': settings.REST_FRAMEWORK['PAGINATE_BY']
        }
    }

    return Response(response)
