# Create your views here.
from django.shortcuts import render
from projects.models import Project, Page

def dashboard(request):
    data = {}
    return render(request, 'projects/dashboard.html', data)

def settings(request):
    data = {}
    return render(request, 'projects/settings.html', data)

def view(request, project_id):
    # Fake project for now (until the model is set up)
    project = Project.objects.get(pk=project_id)

    data = {
        'project': project,
    }
    return render(request, 'projects/view.html', data)

def page_view(request,page_id):
    page = Page.objects.get(pk=page_id)

    data = {
        'page':page
    }
    return render(request,'projects/page_view.html', data)