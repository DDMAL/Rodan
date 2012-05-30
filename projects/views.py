from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from projects.models import Project, Page, Job, Workflow
from projects.forms import ProjectForm, JobForm, WorkflowForm, PageForm, PageUploadForm
from django.http import Http404
from django.conf import settings as django_settings

import logging
import pdb

logger = logging.getLogger('django')

@login_required
def dashboard(request):
    jobs = Job.objects.all()
    workflows = Workflow.objects.all()
    data = {
        'jobs': jobs,
        'workflows': workflows,
        'my_projects': request.user.get_profile().project_set.all(),
    }
    return render(request, 'projects/dashboard.html', data)

def settings(request):
    data = {}
    return render(request, 'projects/settings.html', data)

def view(request, project_id):
    project = Project.objects.get(pk=project_id)
    path = 'uploads/rodan/static/'
    if request.method == "POST":
        
        #page.save()
        #page = Page()
        form = PageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['path_to_image'])
            page = Page.objects.create(image_name=request.FILES['path_to_image'].name,path_to_image=django_settings.MEDIA_ROOT, project=project)
            #page.save()
            #page.image_name = request.FILES['path_to_image']
            project.page_set.add(page)
            #form.save()
    else:
        form = PageUploadForm()
    
    #pdb.set_trace()
    data = {
        'file_upload': True,
        'project': project,
        'user_can_edit': project.is_owned_by(request.user),
        'form': form,
    }
    return render(request, 'projects/view.html', data)

def handle_uploaded_file(f):
    dest = open(django_settings.MEDIA_ROOT + "/" + f.name, 'wb')
    for chunk in f.chunks():
        dest.write(chunk)
    dest.close()

def page_view(request,page_id):
    page = Page.objects.get(pk=page_id)
    
    data = {
        'page': page,
        'project' : page.project,
        'jobs': Job.objects.all(),
    }
    return render(request,'projects/page_view.html', data)

@login_required
def create(request):
    if request.method == 'POST':
        project = Project(rodan_user=request.user.get_profile())
        form = ProjectForm(request.POST, instance=project)
        
        if form.is_valid():
            form.save()
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

def job_view(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    data = {
        'job': job,
    }

    return render(request, 'projects/job_view.html', data)

def workflow_edit(request, workflow_id):
    workflow = get_object_or_404(Workflow, pk=workflow_id)
    if request.method == 'POST':
        form = WorkflowForm(request.POST, instance=workflow)
        
        if form.is_valid():
            form.save()
            return redirect(workflow.get_absolute_url())
        # If there are errors?
    else:
        form = WorkflowForm(instance=workflow)
    
    data = {
        'form': form,
        'action': 'Edit',
        'jobs': Job.objects.all()
    }
    
    return render(request, 'projects/workflow_create.html', data)

@login_required
def workflow_create(request):
    # https://docs.djangoproject.com/en/dev/topics/forms/media/
    # For form-specific javascript files
    if request.method == 'POST':
        workflow = Workflow()
        form = WorkflowForm(request.POST, instance=workflow)
        if form.is_valid():
            form.save()
            return redirect(workflow.get_absolute_url())
    else:
        form = WorkflowForm()
    
    data = {
        'form': form,
        'action': 'Create',
        'jobs': Job.objects.all()
    }
    
    return render(request, 'projects/workflow_create.html', data)

def workflow_view(request, workflow_id):
    workflow = get_object_or_404(Workflow, pk=workflow_id)
    data = {
        'workflow': workflow,
    }
    
    return render(request, 'projects/workflow_view.html', data)

@login_required
def edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    
    # If the user is not one of the owners, show 404
    if not project.is_owned_by(request.user):
        raise Http404
    
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

def upload(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = PageForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            return redirect(project.get_absolute_url())
    else:
        form = PageForm(instance=project)
    
    data = {
        'form': form,
    }
    
    return render(request, 'projects/upload.html', data)
