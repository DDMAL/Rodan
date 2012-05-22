# Create your views here.
from django.shortcuts import render

def dashboard(request):
    # Fake list of projects. Replace this once the model has been defined
    projects = [
        {'name': 'My project', 'description': 'My awesome project', 'slug': 'my-project'},
        {'name': 'Your project', 'description': 'Your terrible project', 'slug': 'your-project'},
    ]

    data = {
        'projects': projects,
    }
    return render(request, 'projects/dashboard.html', data)
