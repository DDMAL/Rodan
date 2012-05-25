from django.shortcuts import render, redirect
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

def create(request):
    if not request.user.is_authenticated():
        return redirect('/signup')

    data = {
        'errors': [],
    }
    if request.method == 'POST':
        name = request.POST.get('name', '')
        description = request.POST.get('description', '')
        if name == '':
            data['errors'].append("You must enter a project name!")

        if not data['errors']:
            project = Project.objects.create(name=name, description=description)
            project.rodan_users.add(request.user.get_profile())
            return redirect(project.get_absolute_url())

    return render(request, 'projects/create.html', data)
