from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from rodan.helpers.workflow import run_workflow


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
            'projects': reverse('project-list', request=request, format=format),
            'workflows': reverse('workflow-list', request=request, format=format),
            'workflowjobs': reverse('workflowjob-list', request=request, format=format),
            'workflowruns': reverse('workflowrun-list', request=request, format=format),
            'runjobs': reverse('runjob-list', request=request, format=format),
            'pages': reverse('page-list', request=request, format=format),
            'jobs': reverse('job-list', request=request, format=format),
            'results': reverse('result-list', request=request, format=format),
            'users': reverse('user-list', request=request, format=format)
    })


@api_view(('GET',))
def kickoff_workflow(request, pk, format=None):
    workflows = run_workflow(pk)
    return Response({
        'success': True,
        'workflows': workflows
    })


@api_view(('GET',))
def run_test_workflow(request, pk, page_id, format=None):
    run_workflow(pk, testing=True, page_id=page_id)
    return Response({'success': True})


@ensure_csrf_cookie
def home(request):
    data = {}
    return render(request, 'base.html', data)
