from django.contrib.auth import (
    authenticate,
    # login,
    # logout
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework import views
from rest_framework import parsers
from rest_framework import renderers
from rest_framework import generics
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer

from rodan.serializers.user import UserSerializer
from rodan.models.user import User


class AuthMeView(generics.RetrieveUpdateAPIView):
    """
    Use this endpoint to retrieve/update user.
    """

    model = User
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self, *a, **k):
        return User.objects.filter(id=self.request.user.id)

    def get_object(self, *args, **kwargs):
        return self.request.user


class AuthTokenView(views.APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer
    model = Token

    def post(self, request):
        email = request.data.get("email", None)
        password = request.data.get("password", None)

        if not email:
            return Response(
                {"is_logged_in": False, "detail": "You must supply an email."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not password:
            return Response(
                {"is_logged_in": False, "detail": "You must supply a password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = authenticate(email=email, password=password)

        if user is not None:
            if user.is_active:
                # authentication successful. Return token.
                token, created = Token.objects.get_or_create(user=user)
                userinfo = UserSerializer(user, context={"request": request})
                data = dict(userinfo.data)  # ReturnDict object is not writable
                data["token"] = token.key
                return Response(data)
            else:
                # user exists, but is not allowed to log in
                return Response(
                    {"is_logged_in": False, "detail": "Account is not activated."}, status=status.HTTP_403_FORBIDDEN
                )
        else:
            # user does not exist. Assume a typo in the email or password
            # and allow the user to re-authenticate
            return Response(
                {"is_logged_in": False, "detail": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED
            )
