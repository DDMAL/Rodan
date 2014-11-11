from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from rodan.serializers.user import UserSerializer, UserListSerializer


class UserList(generics.ListCreateAPIView):
    """
    Returns a list of Users. Accepts POST requests to create a new User.
    A successful POST request will return the newly created User object.

    #### Parameters
    - `username` -- GET & POST.
    - `password` -- GET & POST.
    """
    model = User
    permission_classes = (permissions.IsAdminUser, )
    serializer_class = UserListSerializer

    def get_queryset(self):
        queryset = User.objects.exclude(pk=-1)
        return queryset

    def post(self, request, *args, **kwargs):
        userName = request.DATA.get('username', None)
        userPass = request.DATA.get('password', None)
        user = User.objects.create_user(username=userName, password=userPass)
        if not user:
            return Response({'message': "error creating user"}, status=status.HTTP_200_OK)
        return Response({'username': user.username}, status=status.HTTP_201_CREATED)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Performs operations on a single User instance.
    """
    model = User
    permission_classes = (permissions.IsAdminUser, )
    serializer_class = UserSerializer


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
