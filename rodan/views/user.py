from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import permissions

from rodan.serializers.user import UserSerializer


class UserList(generics.ListCreateAPIView):
    model = User
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    model = User
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    serializer_class = UserSerializer
