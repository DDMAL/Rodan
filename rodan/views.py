from django.shortcuts import render
from projects.views import dashboard


def main(request):
    if request.user.is_authenticated():
        return dashboard(request)
    else:
        return signup(request)

# View to allow users to log in or create accounts
def signup(request):
    return render(request, 'signup.html')
