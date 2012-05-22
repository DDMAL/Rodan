from django.shortcuts import render, redirect
from projects.views import dashboard
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


def main(request):
    if request.user.is_authenticated():
        return redirect('/projects/dashboard')
    else:
        return signup(request)

# View to allow unauthenticate users to log in or create accounts
def signup(request):
    data = {
        'dialog': True,
    }

    if request.POST:
        errors = []
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        email = request.POST.get('email', '')

        # If email is defined, try to create a new user
        if email:
            # Case-insensitive usernames
            if User.objects.filter(username__iexact=username).count() > 0:
                errors.append("This username is already in use. Please find a new one.")
            else:
                User.objects.create_user(username, email, password)
                new_user = authenticate(username=username, password=password)
                login(request, new_user)
                return main(request)
        else:
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return main(request)
            else:
                errors.append("Login error. Wrong password/username?")

        data = {
            'errors': errors,
            'username': username,
            'password': password,
            'email': email,
            'dialog': True, # this shouldn't have to be defined twice
        }

    return render(request, 'signup.html', data)

def logout_view(request):
    if request.user.is_authenticated():
        logout(request)
    return signup(request)
