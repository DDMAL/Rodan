from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import permissions

from rodan.serializers.user import UserSerializer, UserListSerializer


class UserList(generics.ListCreateAPIView):
    model = User
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    serializer_class = UserListSerializer
    def get_queryset(self):
        queryset = User.objects.exclude(pk=-1)
        return queryset


class UserDetail(generics.RetrieveAPIView):
    model = User
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    serializer_class = UserSerializer
