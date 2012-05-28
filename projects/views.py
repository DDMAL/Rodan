from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from projects.models import Project, Page, Job
from projects.forms import ProjectForm, JobForm, WorkflowForm

@login_required
def dashboard(request):
    jobs = Job.objects.all()
    data = {'jobs': jobs}
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

@login_required
def create(request):
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

@login_required
def job_create(request):
    if request.method == 'POST':
        # XXX: Make sure we don't create more than 1 job of the
        # same details.
        job = Job()
        form = JobForm(request.POST, instance=job)

        if form.is_valid():
            form.save()
            return redirect("/projects/dashboard")
    else:
        form = JobForm()

    data = {
        'form': form,
        'action': 'Create'
    }

    return render(request, 'projects/job_create.html', data)

@login_required
def job_edit(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect("/projects/dashboard")
    else:
        form = JobForm(instance=job)

    data = {
        'form': form,
        'action': 'Edit'
    }
    return render(request, 'projects/job_create.html', data)

def workflow_edit(request, workflow_id):
    pass

@login_required
def workflow_create(request):
    # https://docs.djangoproject.com/en/dev/topics/forms/media/
    # For form-specific javascript files
    if request.method == 'POST':
        # XXX: Make sure we don't create more than 1 job of the
        # same details.
        job = Job()
        form = JobForm(request.POST, instance=job)

        if form.is_valid():
            form.save()
            return redirect(job.get_absolute_url())
    else:
        form = WorkflowForm()

    data = {
        'form': form,
        'action': 'Create'
    }

    return render(request, 'projects/workflow_create.html', data)

@login_required
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
