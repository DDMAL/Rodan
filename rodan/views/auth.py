from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework import views
from rest_framework import parsers
from rest_framework import renderers
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer

from rodan.serializers.user import UserSerializer


class SessionStatus(views.APIView):
    permission_classes = ()

    """
    Return session status to see if the user is logged in or they need to authenticate.
    """
    def get(self, request, *args, **kwargs):
        is_auth = request.user.is_authenticated() or request.auth
        if is_auth:
            token = None
            if request.auth:
                token, created = Token.objects.get_or_create(user=request.user)
                token = token.key
            obj = User.objects.get(pk=request.user.id)
            userinfo = UserSerializer(obj, context={'request': request})
            data = dict(userinfo.data)
            data['token'] = token

            return Response(data)
        else:
            return Response({'detail': "User is not logged in"}, status=status.HTTP_401_UNAUTHORIZED)


class SessionAuth(views.APIView):
    """
    Session authentication.

    This will set two cookies, `crsftoken` and `sessionid`.
    These are persistent in your browsing session. "Logging out" will effectively
    delete these cookies, and require to re-authenticate on your next visit.

    #### Parameters
    - username -- Username
    - password -- Password

    #### Example
    `{"username": "admin", "password": "admin"}`
    """
    def post(self, request, *args, **kwargs):
        username = request.DATA.get('username', None)
        password = request.DATA.get('password', None)

        if not username:
            return Response({'detail': "You must supply a username"}, status=status.HTTP_401_UNAUTHORIZED)
        if not password:
            return Response({'detail': "You must supply a password"}, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                # log in successfully
                login(request, user)
                serializer = UserSerializer(user, context={'request': request})
                return Response(serializer.data)
            else:
                # user exists, but is not allowed to log in
                return Response({"is_logged_in": False}, status=status.HTTP_403_FORBIDDEN)
        else:
            # user does not exist. Assume a typo in the username or password and allow the user to re-authenticate
            return Response({"is_logged_in": False}, status=status.HTTP_401_UNAUTHORIZED)


class SessionClose(views.APIView):
    """
    POST to log out. This will clear `sessionid`.
    """
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            logout(request)
            return Response({'detail': "User was successfully logged out"})
        else:
            return Response({'detail': "Access denied"}, status=status.HTTP_403_FORBIDDEN)


class ObtainAuthToken(views.APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer
    model = Token

    def post(self, request):
        username = request.DATA.get('username', None)
        password = request.DATA.get('password', None)

        if not username:
            return Response({'detail': "You must supply a username"}, status=status.HTTP_401_UNAUTHORIZED)
        if not password:
            return Response({'detail': "You must supply a password"}, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                # authentication successful. Return token.
                token, created = Token.objects.get_or_create(user=user)
                userinfo = UserSerializer(user, context={'request': request})
                data = dict(userinfo.data)  # ReturnDict object is not writable
                data['token'] = token.key
                return Response(data)
            else:
                # user exists, but is not allowed to log in
                return Response({"is_logged_in": False}, status=status.HTTP_403_FORBIDDEN)
        else:
            # user does not exist. Assume a typo in the username or password and allow the user to re-authenticate
            return Response({"is_logged_in": False}, status=status.HTTP_401_UNAUTHORIZED)
