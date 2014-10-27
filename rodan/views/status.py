from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rodan.celery import app

class StatusView(APIView):
    permission_classes = (permissions.IsAdminUser, )

    def get(self, request, format=None):
        inspect = app.control.inspect()
        return Response(inspect.active())
