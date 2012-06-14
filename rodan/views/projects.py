from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from rodan.models.projects import Project, Workflow, Job, JobItem
from rodan.models.results import Result
from rodan.forms.projects import ProjectForm
import random


@login_required
def dashboard(request):
    data = {
        'my_projects': request.user.get_profile().project_set.all(),
    }

    return render(request, 'projects/dashboard.html', data)


@login_required
def create(request):
    data = {}

    return render(request, 'projects/create.html', data)


def view(request, project_id):
    done = bool(request.GET.get('done', False))
    project = get_object_or_404(Project, pk=project_id)

    # This is a upser hacky way of doing it. If you can improve this, please do
    all_jobs = Job.objects.all()
    available_jobs = set([])
    user = request.user.get_profile() if request.user.is_authenticated() else None
    for page in project.page_set.all():
        page_job = page.get_next_job(user=user)
        available_jobs.add(page_job)

    # Create a dict: key = job, value = availability for this project
    jobs = {}
    for job in all_jobs:
        jobs[job] = job in available_jobs

    data = {
        'done': done,
        'user_can_edit': project.is_owned_by(request.user),
        'project': project,
        'num_pages': project.page_set.count(),
        'jobs': jobs,
    }

    return render(request, 'projects/view.html', data)


@login_required
def edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    # If the user isn't the projects owner, show a 404
    if not project.is_owned_by(request.user):
        raise Http404

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            form.save()
            return redirect(project.get_absolute_url())
    else:
        form = ProjectForm(instance=project)

    data = {
        'project': project,
        'form': form,
    }

    return render(request, 'projects/edit.html', data)


@login_required
def add_pages(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    data = {
        'project': project,
    }

    if not project.is_owned_by(request.user):
        raise Http404

    return render(request, 'projects/add_pages.html', data)


# Will show you a random page from this project, with this slug
# If project_id == 0, then use all projects
@login_required
def task(request, job_slug, project_id=0):
    if project_id == 0:
        # Choose a random project!
        project = random.choice(Project.objects.all())
    else:
        project = get_object_or_404(Project, pk=project_id)

    job = get_object_or_404(Job, slug=job_slug)

    # Don't allow users to view this for automatic jobs
    if job.get_object().is_automatic:
        raise Http404

    # Now, try to find a page in this project that has this job next
    # (May have been started by the current user but never finished)
    rodan_user = request.user.get_profile()
    possible_pages = [page for page in project.page_set.all() if page.get_next_job(user=rodan_user) == job]
    # No pages that need this job. Show a 404 for now.
    if not possible_pages:
        raise Http404
    page = random.choice(possible_pages)

    # Start the job, noting this user (create the result, with no end time)
    # If the job has already been started by this user, do nothing
    page.start_next_job(user=rodan_user)

    job_object = job.get_object()
    view_data = job.get_view()
    data = {
        'project': project,
        'job': job,
        'page': page,
        'template': view_data[0],
        'context': view_data[1]
    }

    return render(request, 'projects/task.html', data)
