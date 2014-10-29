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
    """
    Return session status to see if the user is logged in or they need to authenticate.
    """
    def get(self, request, *args, **kwargs):
        is_auth = request.user.is_authenticated()
        if is_auth:
            obj = User.objects.get(pk=request.user.id)
            serializer = UserSerializer(obj, context={'request': request})
            return Response(serializer.data)
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
                # user exists, but is inactive
                return Response({"is_logged_in": False}, status=status.HTTP_403_FORBIDDEN)
        else:
            # user does not exist
            return Response({"is_logged_in": False}, status=status.HTTP_403_FORBIDDEN)


class SessionClose(views.APIView):
    """
    Logging out.

    This will clear `sessionid`.
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
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            token, created = Token.objects.get_or_create(user=serializer.object['user'])
            userinfo = UserSerializer(serializer.object['user'], context={'request': request})
            info_with_token = userinfo.data['token'] = token.key
            return Response(userinfo.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

