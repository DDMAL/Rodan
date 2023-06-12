from __future__ import absolute_import
from rodan.models import UserPreference
from rodan.serializers.userpreference import (
    UserPreferenceListSerializer,
    UserPreferenceSerializer,
)
from rodan.exceptions import CustomAPIException
from rodan.permissions import CustomObjectPermissions

from django.contrib.auth.models import User
from django.core.urlresolvers import Resolver404, resolve

from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status

import six.moves.urllib.parse


class UserPreferenceList(generics.ListCreateAPIView):
    model = UserPreference
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    _ignore_model_permissions = True
    serializer_class = UserPreferenceListSerializer
    queryset = UserPreference.objects.all()

    def get_queryset(self):
        # a user only can view its own userpreference unless it is a superuser
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        return UserPreference.objects.filter(user=user)

    def post(self, request, *args, **kwargs):
        user_url = request.data.get("user", None)
        if user_url:
            try:
                path = six.moves.urllib.parse.urlparse(user_url).path
                match = resolve(path)
                user_pk = match.kwargs.get("pk")
            except (Resolver404, User.DoesNotExist):
                raise CustomAPIException(
                    "You need to send the url of a User to create its UserPreference.",
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            raise CustomAPIException(
                "You need to identify a User to create its UserPreference.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        userpreference_obj = UserPreference(
            user_id=user_pk, send_email=request.data.get("send_email", False)
        )
        userpreference_obj.save()
        d = UserPreferenceSerializer(
            userpreference_obj, context={"request": request}
        ).data
        return Response(d, status=status.HTTP_201_CREATED)


class UserPreferenceDetail(generics.RetrieveUpdateDestroyAPIView):
    model = UserPreference
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    _ignore_model_permissions = True
    serializer_class = UserPreferenceSerializer
    queryset = UserPreference.objects.all()
