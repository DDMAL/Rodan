from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse


@api_view(("GET",))
def session_status(request, format=None):
    """ Get session status to see if the user is logged in or they need to authenticate. """
    is_auth = request.user.is_authenticated()
    if is_auth:
        # user is already authenticated
        user = reverse('user-detail', request=request, format=format, args=(request.user.pk,))
        return Response({"is_logged_in": True, 'user': user})
    else:
        # user is not authenticated, but can try again
        return Response({"is_logged_in": False}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(("GET", "POST"))
def session_auth(request, format=None):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            # log in successfully
            login(request, user)
            user = reverse('user-detail', request=request, format=format, args=(request.user.pk,))
            return Response({"is_logged_in": True, 'user': user})
        else:
            # user exists, but is inactive
            return Response({"is_logged_in": False}, status=status.HTTP_403_FORBIDDEN)
    else:
        # user does not exist
        return Response({"is_logged_in": False}, status=status.HTTP_403_FORBIDDEN)
