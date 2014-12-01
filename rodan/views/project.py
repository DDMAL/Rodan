from rest_framework import generics
from rest_framework import permissions
from guardian.shortcuts import get_objects_for_user

from rodan.models.project import Project
from rodan.serializers.project import ProjectSerializer
from rodan.serializers.user import UserSerializer


class ProjectList(generics.ListCreateAPIView):
    """
    Returns a list of Projects that the user has permissions to view. Accepts a POST
    request with a data body to create a new Project. POST requests will return the
    newly-created Project object.
    """
    model = Project
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProjectSerializer
    queryset = Project.objects.all() # [TODO] restrict to the user's projects?

    def get_queryset(self):
        queryset = get_objects_for_user(self.request.user, 'rodan.view_projects')
        return queryset

    def create(self, request, *a, **k):  # [TODO] ugly
        user_obj = UserSerializer(request.user, context={'request': request}).data
        request.DATA['creator'] = user_obj['url']
        return super(ProjectList, self).create(request, *a, **k)


class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Performs operations on a single Project instance.
    """
    model = Project
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProjectSerializer
    queryset = Project.objects.all() # [TODO] restrict to the user's projects?
