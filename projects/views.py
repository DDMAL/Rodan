from django.shortcuts import render, redirect, get_object_or_404
from projects.models import Project, Page
from projects.forms import ProjectForm

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

    if request.method == 'POST':
        project = Project()
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            form.save()
            project.rodan_users.add(request.user.get_profile())
            return redirect(project.get_absolute_url())
    else:
        form = ProjectForm()

    data = {
        'form': form,
    }

    return render(request, 'projects/create.html', data)

def edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect(project.get_absolute_url())
    else:
        form = ProjectForm(instance=project)

    data = {
        'form': form,
    }

    return render(request, 'projects/edit.html', data)
