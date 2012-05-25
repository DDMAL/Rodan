from django.shortcuts import render, redirect
from projects.views import dashboard
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


# The statistics and everything
def home(request):
    workers = {
        # Format: Job: number of things in queue
        'Binarisation': 4,
        'Recognition': 5,
        'Segmentation': 1,
        'Cropping': 0,
        'Whatever': 1,
        'Fake worker': 3,
        'Another fake': 1,
    }

    data = {
        'num_projects': 100,
        'num_pages': 1000,
        'total_size': '5421 GB',
        'workers': workers,
    }

    return render(request, 'home.html', data)

# View to allow unauthenticate users to log in or create accounts
def signup(request):
    # If the user is already logged in, go to dashboard
    if request.user.is_authenticated():
        return redirect('/projects/dashboard')

    data = {}
    if request.POST:
        errors = []
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        email = request.POST.get('email', '')

        # Make sure the username and password are specified first of fall
        if not username:
            errors.append("Please enter a username.")

        if not password:
            errors.append("Please enter a password.")

        # If email is defined, try to create a new user
        if email:
            # Case-insensitive usernames
            if User.objects.filter(username__iexact=username).count() > 0:
                errors.append("This username is already in use. Please find a new one.")

            if not errors:
                User.objects.create_user(username, email, password)
                new_user = authenticate(username=username, password=password)
                login(request, new_user)
                return redirect('/projects/dashboard')
        else:
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/projects/dashboard')
            else:
                errors.append("Login error. Wrong password/username?")

        data = {
            'errors': errors,
            'username': username,
            'password': password,
            'email': email,
        }

    return render(request, 'signup.html', data)

def logout_view(request):
    if request.user.is_authenticated():
        logout(request)
    return redirect('/')
