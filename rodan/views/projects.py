from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from rodan.models.projects import Project, Workflow, Job
from rodan.models.results import Result
from rodan.forms.projects import ProjectForm

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
    project = get_object_or_404(Project, pk=project_id)

    # This is a upser hacky way of doing it. If you can improve this, please do
    all_jobs = Job.objects.all()
    available_jobs = set([])
    project_workflows = Workflow.objects.filter(page__project=project).all()
    for workflow in project_workflows:
        for page in project.page_set.all():
            for job_item in workflow.jobitem_set.all():
                try:
                    result = Result.objects.get(job_item=job_item, page=page)
                    if result.end_total_time is None:
                        # This job has been started, but has not been finished
                        # If the user is the one who started it, show it, jic
                        if result.user == request.user.get_profile():
                            available_jobs.add(job_item.job)
                            break
                    else:
                        # This job has already finished. Go onto the next one.
                        continue
                except Result.DoesNotExist:
                    # This one has not even been started yet. Cool.
                    available_jobs.add(job_item.job)
                    break

    # Create a dict: key = job, value = availability for this project
    jobs = {}
    for job in all_jobs:
        jobs[job] = job in available_jobs

    data = {
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
def task(request, job_slug, project_id=0):
    if project_id > 0:
        project = get_object_or_404(Project, pk=project_id)
        job = get_object_or_404(Job, slug=job_slug)
        print job

        # Now, try to find a page in this project that has this job next
        # Later ...

        data = {
            'project': project,
            'job': job,
        }

        return render(request, 'projects/task.html', data)
    else:
        print "NOT IMPLEMENTED YET"
        raise Http404
