from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from guardian.shortcuts import get_objects_for_user

from rodan.helpers.check_uuid import check_uuid
from rodan.models.project import Project
from rodan.serializers.project import ProjectSerializer, ProjectListSerializer


class ProjectList(generics.ListCreateAPIView):
    """
    Returns a list of projects that the user has permissions to view. Accepts a POST request with a data body to create a new project. POST requests will return the newly-created project object.
    """
    model = Project
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProjectListSerializer
    paginate_by = None

    def get_queryset(self):
        # queryset = Project.objects.all()
        queryset = get_objects_for_user(self.request.user, 'rodan.view_projects')
        return queryset


class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Performs operations on a single project instance.
    """
    model = Project
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProjectSerializer

    def get(self, request, pk, *args, **kwargs):
        if not check_uuid(pk):
            return Response({'message': "You must supply a valid UUID identifier"}, status=status.HTTP_400_BAD_REQUEST)
        return self.retrieve(request, *args, **kwargs)
