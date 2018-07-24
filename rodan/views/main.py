from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import permissions

import rodan
from rodan.jobs import package_versions


class APIRoot(APIView):

    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        """
        Browse all APIs of Rodan server.

        Note: this browsable API only supports HTTP basic authentication. When logging in
        is required, your browser will prompt the username and password. To log out,
        you need to quit your browser, or provide a wrong username/password combination
        in URL as: `http://fakeusr:fakepwd@localhost:8000`.

        HTTP basic authentication is disabled in production mode. Only token authentication
        will be allowed. HTTP basic authentication is a workaround for this browsable
        API and Django [admin](/admin/).
        """
        response = {
            "routes": {
                "projects": reverse("project-list", request=request, format=format),
                "workflows": reverse("workflow-list", request=request, format=format),
                "workflowjobs": reverse(
                    "workflowjob-list", request=request, format=format
                ),
                "workflowjobgroups": reverse(
                    "workflowjobgroup-list", request=request, format=format
                ),
                "workflowruns": reverse(
                    "workflowrun-list", request=request, format=format
                ),
                "runjobs": reverse("runjob-list", request=request, format=format),
                "jobs": reverse("job-list", request=request, format=format),
                "users": reverse("user-list", request=request, format=format),
                "userpreferences": reverse(
                    "userpreference-list", request=request, format=format
                ),
                "resultspackages": reverse(
                    "resultspackage-list", request=request, format=format
                ),
                "connections": reverse(
                    "connection-list", request=request, format=format
                ),
                "outputporttypes": reverse(
                    "outputporttype-list", request=request, format=format
                ),
                "outputports": reverse(
                    "outputport-list", request=request, format=format
                ),
                "inputporttypes": reverse(
                    "inputporttype-list", request=request, format=format
                ),
                "inputports": reverse("inputport-list", request=request, format=format),
                "resources": reverse("resource-list", request=request, format=format),
                "resourcelists": reverse(
                    "resourcelist-list", request=request, format=format
                ),
                "resourcetypes": reverse(
                    "resourcetype-list", request=request, format=format
                ),
                "outputs": reverse("output-list", request=request, format=format),
                "inputs": reverse("input-list", request=request, format=format),
                "taskqueue-active": reverse(
                    "taskqueue-active", request=request, format=format
                ),
                "taskqueue-scheduled": reverse(
                    "taskqueue-scheduled", request=request, format=format
                ),
                "taskqueue-status": reverse(
                    "taskqueue-status", request=request, format=format
                ),
                # 'taskqueue-config': reverse('taskqueue-config', request=request, format=format),
                "workflowjobcoordinatesets": reverse(
                    "workflowjobcoordinateset-list", request=request, format=format
                ),
                "workflowjobgroupcoordinatesets": reverse(
                    "workflowjobgroupcoordinateset-list", request=request, format=format
                ),
                "auth-me": reverse("auth-me", request=request, format=format),
                "auth-register": reverse(
                    "auth-register", request=request, format=format
                ),
                "auth-token": reverse("auth-token", request=request, format=format),
                "auth-reset-token": reverse(
                    "auth-reset-token", request=request, format=format
                ),
                "auth-change-password": reverse(
                    "auth-change-password", request=request, format=format
                ),
            },
            "configuration": {
                "page_length": settings.REST_FRAMEWORK["PAGE_SIZE"],
                "job_packages": package_versions,
            },
            "version": rodan.__version__,
        }
        return Response(response)
