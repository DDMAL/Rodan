from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from rodan.permissions import CustomObjectPermissions
from rodan.serializers.user import UserSerializer, UserListSerializer

import django_filters


class UserList(generics.ListCreateAPIView):
    """
    Returns a list of Users. Accepts POST requests to create a new User.
    A successful POST request will return the newly created User object.

    #### Parameters
    - `username` -- GET & POST.
    - `password` -- GET & POST.
    """

    model = User
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    _ignore_model_permissions = True
    serializer_class = UserListSerializer

    class filter_class(django_filters.FilterSet):
        # username__in = django_filters.MethodFilter()

        # def filter_username__in(self, q, v):
        #     vs = v.split(",")
        #     return q.filter(username__in=vs)

        username__in = django_filters.filters.CharFilter(method='filter_username__in')

        def filter_username__in(self, qs, name, value):
            return qs.filter(**{name: value})

        class Meta:
            model = User
            fields = {"username": ["in"]}

    def get_queryset(self):
        queryset = User.objects.exclude(pk=-1)
        return queryset

    def post(self, request, *args, **kwargs):
        userName = request.data.get("username", None)
        userPass = request.data.get("password", None)
        user = User.objects.create_user(username=userName, password=userPass)
        if not user:
            return Response(
                {"message": "error creating user"}, status=status.HTTP_200_OK
            )
        return Response({"username": user.username}, status=status.HTTP_201_CREATED)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Performs operations on a single User instance.
    """

    model = User
    permission_classes = (permissions.IsAuthenticated,)
    _ignore_model_permissions = True
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.exclude(pk=-1)
        return queryset

    def get(self, request, *args, **kwargs):
        # A user can only view it's own user detail unless it's a superuser
        if request.user.id == int(kwargs["pk"]) or request.user.is_superuser:
            return super(UserDetail, self).get(request, *args, **kwargs)
        else:
            raise PermissionDenied("You cannot view this user's details")


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
