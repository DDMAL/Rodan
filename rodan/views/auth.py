from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import views
from rest_framework import generics

from rodan.serializers.user import UserSerializer


class SessionStatus(views.APIView):
    """ Get session status to see if the user is logged in or they need to authenticate. """
    model = User
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        is_auth = request.user.is_authenticated()
        if is_auth:
            obj = User.objects.get(pk=request.user.id)
            serializer = UserSerializer(obj)
            return Response(serializer.data)
        else:
            return Response({'detail': "User is not logged in"}, status=status.HTTP_401_UNAUTHORIZED)


class SessionAuth(generics.CreateAPIView):
    # def get(self, request, *args, **kwargs):
    #     print "GET method called"
    #     return Response({})

    def post(self, request, *args, **kwargs):
        print "POST method called"

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
                return Response(UserSerializer(user).data)
            else:
                # user exists, but is inactive
                return Response({"is_logged_in": False}, status=status.HTTP_403_FORBIDDEN)
        else:
            # user does not exist
            return Response({"is_logged_in": False}, status=status.HTTP_403_FORBIDDEN)

# @api_view(("GET", "POST"))
# def session_auth(request, format=None):
#     username = request.POST.get('username', None)
#     password = request.POST.get('password', None)

#     if not username:
#         return Response({'detail': "You must supply a username"}, status=status.HTTP_401_UNAUTHORIZED)
#     if not password:
#         return Response({'detail': "You must supply a password"}, status=status.HTTP_401_UNAUTHORIZED)

#     user = authenticate(username=username, password=password)
#     if user is not None:
#         if user.is_active:
#             # log in successfully
#             login(request, user)
#             return Response(UserSerializer(user).data)
#         else:
#             # user exists, but is inactive
#             return Response({"is_logged_in": False}, status=status.HTTP_403_FORBIDDEN)
#     else:
#         # user does not exist
#         return Response({"is_logged_in": False}, status=status.HTTP_403_FORBIDDEN)
