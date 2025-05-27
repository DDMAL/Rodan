from rest_framework import generics
from rest_framework import permissions, exceptions
from rest_framework.response import Response
from rodan.models.project import Project, User
from rodan.serializers.project import ProjectListSerializer, ProjectDetailSerializer
from rodan.permissions import CustomObjectPermissions
from django.conf import settings
from django.db.models import Q
from celery import registry


class ProjectList(generics.ListCreateAPIView):
    """
    Returns a list of Projects that the user has permissions to view. Accepts a POST
    request with a data body to create a new Project. POST requests will return the
    newly-created Project object.
    """

    permission_classes = (permissions.IsAuthenticated,)
    #queryset = Project.objects.all()
    serializer_class = ProjectListSerializer
    filter_fields = {
        "updated": ["lt", "gt"],
        "uuid": ["exact"],
        "created": ["lt", "gt"],
        "creator": ["exact"],
        "name": ["exact", "icontains"],
        "description": ["exact", "icontains"],
    }

    def get_queryset(self):
        # Retrieve the base queryset
        queryset = Project.objects.all()

        # Apply additional filtering based on user permissions
        user = self.request.user
        if not user.is_superuser:
            # Filter projects based on the creator or user's permissions logic
            queryset = queryset.filter(
                Q(creator=user) | Q(admin_group__user=user) | Q(worker_group__user=user)
            )
        return queryset.order_by('-created')

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

        new_users = [user for user in users if user not in p.admin_group.user_set.all()]

        p.admin_group.user_set.clear()
        p.admin_group.user_set.add(*users)
        if p.creator:
            p.admin_group.user_set.add(p.creator)
        
        if (getattr(settings, "EMAIL_USE", False)):
            self.send_email(new_users)

        return Response(p.admin_group.user_set.values_list("username", flat=True))

    def patch(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)
    
    def send_email(self, new_users):
        project = self.get_object()
        user = self.request.user

        to = [user.email for user in new_users if user.email and user.user_preference.send_email]
        email_template = "emails/added_to_project.html"
        context = {"project_name": project.name, "role": "admin", "adder": user.username}
        
        registry.tasks["rodan.core.send_templated_email"].apply_async((to, email_template, context))


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
            self.request.user != obj.creator and not self.request.user.groups.filter(
                id=obj.admin_group.id
            ).exists()
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

        new_users = [user for user in users if user not in p.admin_group.user_set.all()]

        p.worker_group.user_set.clear()
        p.worker_group.user_set.add(*users)

        self.send_email(new_users)

        return Response(p.worker_group.user_set.values_list("username", flat=True))

    def patch(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)
    
    def send_email(self, new_users):
        project = self.get_object()
        user = self.request.user

        to = [user.email for user in new_users if user.email and user.user_preference.send_email]
        email_template = "emails/added_to_project.html"
        context = {"project_name": project.name, "role": "worker", "adder": user.username}
        
        registry.tasks["rodan.core.send_templated_email"].apply_async((to, email_template, context))
