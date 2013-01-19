from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rodan.forms.users import SignupLoginForm


@login_required
def home(request):
    data = {
    }
    return render(request, 'main/home.html', data)


# View to allow unauthenticated users to log in or create accounts
def signup(request):
    # path = request.GET.get('next', '') or reverse('dashboard')

    if request.user.is_authenticated():
        return redirect('dashboard')

    if not request.POST:
        form = SignupLoginForm()
        data = {
            'form': form,
            'form_action': request.get_full_path()
        }
        return render(request, 'main/signup.html', data)
    else:
        form = SignupLoginForm(request.POST)
        if not form.is_valid():
            return 0  # raise an error.
        else:
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('dashboard')


def logout_view(request):
    if request.user.is_authenticated():
        logout(request)
    return redirect('/')
