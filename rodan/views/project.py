from rest_framework import generics
from rest_framework import permissions
from guardian.shortcuts import get_objects_for_user

from rodan.paginators.pagination import PaginationSerializer
from rodan.models.project import Project
from rodan.serializers.project import ProjectListSerializer, ProjectDetailSerializer
from rodan.serializers.user import UserSerializer


class ProjectList(generics.ListCreateAPIView):
    """
    Returns a list of Projects that the user has permissions to view. Accepts a POST
    request with a data body to create a new Project. POST requests will return the
    newly-created Project object.
    """
    model = Project
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProjectListSerializer
    pagination_serializer_class = PaginationSerializer
    queryset = Project.objects.all() # [TODO] restrict to the user's projects?

    def get_queryset(self):
        queryset = get_objects_for_user(self.request.user, 'rodan.view_projects')
        return queryset

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Performs operations on a single Project instance.
    """
    model = Project
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProjectDetailSerializer
    queryset = Project.objects.all() # [TODO] restrict to the user's projects?
