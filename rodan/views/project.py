from rest_framework import generics
from rest_framework import permissions

from rodan.models.project import Project
from rodan.serializers.project import ProjectSerializer


class ProjectList(generics.ListCreateAPIView):
    model = Project
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    serializer_class = ProjectSerializer

    def get_queryset(self):
        queryset = Project.objects.all()
        return queryset


class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Project
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    serializer_class = ProjectSerializer

    def pre_save(self, obj):
        obj.creator = self.request.user
