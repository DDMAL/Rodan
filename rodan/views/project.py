from rest_framework import generics
from rest_framework import permissions, exceptions
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from rodan.models.project import Project
from rodan.serializers.project import ProjectListSerializer, ProjectDetailSerializer
from rodan.permissions import CustomObjectPermissions


class ProjectList(generics.ListCreateAPIView):
    """
    Returns a list of Projects that the user has permissions to view. Accepts a POST
    request with a data body to create a new Project. POST requests will return the
    newly-created Project object.
    """

    permission_classes = (permissions.IsAuthenticated,)
    queryset = Project.objects.all()
    serializer_class = ProjectListSerializer
    filter_fields = {
        "updated": ["lt", "gt"],
        "uuid": ["exact"],
        "created": ["lt", "gt"],
        "creator": ["exact"],
        "name": ["exact", "icontains"],
        "description": ["exact", "icontains"],
    }

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Performs operations on a single Project instance.
    """

    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    _ignore_model_permissions = True
    queryset = Project.objects.all()
    serializer_class = ProjectDetailSerializer


class ProjectDetailAdmins(generics.GenericAPIView):
    """
    Retrieve and update project admin user list. Only open to project creator.
    """

    queryset = Project.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        # for rest browsable API displaying the PUT/PATCH form
        from rest_framework import serializers

        class DummySerializer(serializers.Serializer):
            pass  # empty class

        return DummySerializer

    def check_object_permissions(self, request, obj):
        if self.request.user != obj.creator:
            raise exceptions.PermissionDenied()

    def get(self, request, *args, **kwargs):
        p = self.get_object()
        return Response(p.admin_group.user_set.values_list("username", flat=True))

    def put(self, request, *args, **kwargs):
        p = self.get_object()
        users = []
        for u_info in request.data:
            try:
                user = User.objects.get(username=u_info)
            except User.DoesNotExist:
                raise exceptions.ValidationError(
                    detail={"detail": "User {0} does not exist.".format(u_info)}
                )
            users.append(user)
        p.admin_group.user_set.clear()
        p.admin_group.user_set.add(*users)
        if p.creator:
            p.admin_group.user_set.add(p.creator)
        return Response(p.admin_group.user_set.values_list("username", flat=True))

    def patch(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)


class ProjectDetailWorkers(generics.GenericAPIView):
    """
    Retrieve and update project worker user list. Only open to project creator and admin.
    """

    queryset = Project.objects.all()

    def get_serializer_class(self):
        # for rest browsable API displaying the PUT/PATCH form
        from rest_framework import serializers

        class DummySerializer(serializers.Serializer):
            pass  # empty class

        return DummySerializer

    def check_object_permissions(self, request, obj):
        if (
            self.request.user != obj.creator
            and not self.request.user.groups.filter(id=obj.admin_group.id).exists()
        ):
            raise exceptions.PermissionDenied()  # not in project admin nor as creator

    def get(self, request, *args, **kwargs):
        p = self.get_object()
        return Response(p.worker_group.user_set.values_list("username", flat=True))

    def put(self, request, *args, **kwargs):
        p = self.get_object()
        users = []
        for u_info in request.data:
            try:
                user = User.objects.get(username=u_info)
            except User.DoesNotExist:
                raise exceptions.ValidationError(
                    detail={"detail": "User {0} does not exist.".format(u_info)}
                )
            users.append(user)
        p.worker_group.user_set.clear()
        p.worker_group.user_set.add(*users)
        return Response(p.worker_group.user_set.values_list("username", flat=True))

    def patch(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)
