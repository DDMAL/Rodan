# Create your views here.
from django.shortcuts import render

def dashboard(request):
    data = {}
    return render(request, 'projects/dashboard.html', data)

def create(request):
    data = {}
    return render(request, 'projects/create.html', data)

def settings(request):
    data = {}
    return render(request, 'projects/settings.html', data)

def status(request):
    data = {}
    return render(request, 'projects/status.html', data)

def view(request, project_id):
    # Fake project for now (until the model is set up)
    project = {
        'name': 'Project %d' % int(project_id),
        'description': 'Fake description',
        'id': project_id,
    }

    data = {
        'project': project,
    }
    return render(request, 'projects/view.html', data)
