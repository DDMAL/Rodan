from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

from rest_framework import generics
from rest_framework import permissions
from rest_framework.authtoken.models import Token

from rodan.serializers.user import UserSerializer, UserListSerializer


class UserList(generics.ListAPIView):
    model = User
    permission_classes = (permissions.IsAdminUser, )
    serializer_class = UserListSerializer
    paginate_by = None

    def get_queryset(self):
        queryset = User.objects.exclude(pk=-1)
        return queryset


class UserDetail(generics.RetrieveAPIView):
    model = User
    permission_classes = (permissions.IsAdminUser, )
    serializer_class = UserSerializer


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
