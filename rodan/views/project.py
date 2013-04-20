from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from rodan.helpers.check_uuid import check_uuid
from rodan.models.project import Project
from rodan.serializers.project import ProjectSerializer, ProjectListSerializer


class ProjectList(generics.ListCreateAPIView):
    model = Project
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    serializer_class = ProjectListSerializer

    def get_queryset(self):
        queryset = Project.objects.all()
        return queryset

    def post(self, request, *args, **kwargs):
        print request.DATA
        return self.create(request, *args, **kwargs)


class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Project
    permission_classes = (permissions.AllowAny, )
    serializer_class = ProjectSerializer

    def get(self, request, pk, *args, **kwargs):
        if not check_uuid(pk):
            return Response({'message': "You must supply a valid UUID identifier"}, status=status.HTTP_400_BAD_REQUEST)
        return self.retrieve(request, *args, **kwargs)

    def pre_save(self, obj):
        obj.creator = self.request.user
