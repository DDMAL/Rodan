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
        'errors': [],
    }

    if request.POST:
        # Try to log the user in
        if 'login' in request.POST:
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/projects/dashboard')
            else:
                data['errors'].append("Login error. Wrong password/username?")

    return render(request, 'signup.html', data)

def logout_view(request):
    if request.user.is_authenticated():
        logout(request)
    return signup(request)
