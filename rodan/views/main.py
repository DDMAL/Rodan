from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, models
from rodan.forms.users import SignupLoginForm
from django.core.urlresolvers import reverse


# The statistics and everything
def home(request):
    workers = [
        # Format: Job: number of things in queue
        ('Cropping', 1),
        ('Rotation', 2),
        ('Binarisation', 0),
        ('Despeckling', 2),
        ('Staff finding', 1),
        ('Segmentation', 1),
        ('Classification', 0),
        ('MEI correction', 0),
        ('Solr indexing', 1),
        ('Diva preprocessing', 0),
    ]

    data = {
        'num_projects': 100,
        'num_pages': 1000,
        'total_size': '5421 GB',
        'workers': workers,
    }

    return render(request, 'main/home.html', data)


# View to allow unauthenticated users to log in or create accounts
def signup(request):
    path = request.GET.get('next', '') or reverse('dashboard')

    if request.user.is_authenticated():
        return redirect(path)

    if request.POST:
        form = SignupLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # If the email is defined, try to create a new user
            if email:
                # Everything is fine, go ahead and create
                models.User.objects.create_user(username, email, password)
                new_user = authenticate(username=username, password=password)
                login(request, new_user)
                return redirect(path)
            else:
                # Trying to log in an existing user
                user = authenticate(username=username, password=password)
                login(request, user)
                return redirect(path)
    else:
        form = SignupLoginForm()

    data = {
        'form': form,
        'form_action': request.get_full_path(),
    }

    return render(request, 'main/signup.html', data)


def logout_view(request):
    if request.user.is_authenticated():
        logout(request)
    return redirect('/')
