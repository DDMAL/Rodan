from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rodan.celery import app


class TaskQueueActiveView(APIView):
    """
    Returns the list of active Celery tasks.
    """

    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, format=None):
        inspect = app.control.inspect()
        return Response(inspect.active())


class TaskQueueConfigView(APIView):
    """
    Returns the config of Celery queue.
    """

    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, format=None):
        inspect = app.control.inspect()
        return Response(inspect.conf())


class TaskQueueScheduledView(APIView):
    """
    Returns the list of scheduled Celery tasks.
    """

    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, format=None):
        inspect = app.control.inspect()
        return Response(inspect.scheduled())


class TaskQueueStatusView(APIView):
    """
    Returns the status of Celery queue.
    """

    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, format=None):
        inspect = app.control.inspect()
        return Response(inspect.stats())
