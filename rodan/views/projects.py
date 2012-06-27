import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.conf import settings
from django.core.urlresolvers import reverse

from rodan.models.projects import Project, Workflow, Job, JobItem, Page
from rodan.models.results import Result
from rodan.forms.projects import ProjectForm, UploadFileForm
from rodan.utils import rodan_view


@login_required
def dashboard(request):
    all_jobs = Job.objects.all()
    available_jobs = {}
    user = request.user.get_profile() if request.user.is_authenticated() else None
    pages = list(Page.objects.all())
    random.shuffle(pages)

    for page in pages:
        if page.workflow and page.workflow.has_started:
            page_job = page.get_next_job(user=user)
            if page_job:
                available_jobs[page_job.slug] = page.project.id

    jobs = []
    for job in all_jobs:
        jobs.append((job, job.slug in available_jobs, available_jobs.get(job.slug, '')))

    data = {
        'my_projects': request.user.get_profile().project_set.all(),
        'jobs': jobs,
    }

    return render(request, 'projects/dashboard.html', data)


@login_required
def create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.creator = request.user.get_profile()
            project.save()
            return redirect(project)
    else:
        form = ProjectForm()

    data = {
        'form': form,
    }

    return render(request, 'projects/create.html', data)


@rodan_view(Project)
def view(request, project):
    done = bool(request.GET.get('done', False))

    # This is a super hacky way of doing it. If you can improve this, please do
    all_jobs = Job.objects.all()
    available_jobs = set([])
    user = request.user.get_profile() if request.user.is_authenticated() else None
    for page in project.page_set.all():
        if page.workflow and page.workflow.has_started:
            page_job = page.get_next_job(user=user)
            available_jobs.add(page_job)

    # Create a dict: key = job, value = availability for this project
    jobs = []
    for job in all_jobs:
        jobs.append((job, job in available_jobs, project.id))

    data = {
        'done': done,
        'user_can_edit': project.is_owned_by(request.user),
        'project': project,
        'num_pages': project.page_set.count(),
        'jobs': jobs,
    }

    return ('View', data)

@login_required
@rodan_view(Project)
def edit(request, project):
    submits = {
        'Save and return to dashboard': ('dashboard', None),
        'Save and continue to image upload': ('upload', [project.id],),
    }

    # If the user isn't the projects owner, show a 404
    if not project.is_owned_by(request.user):
        raise Http404

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            form.save()

            # Figure out where to go next
            submit_value = request.POST.get('action', '')
            redirect_view, redirect_args = submits.get(submit_value, ('dashboard', None))
            return redirect(reverse(redirect_view, args=redirect_args))
    else:
        form = ProjectForm(instance=project)

    data = {
        'project': project,
        'form': form,
        'submits': submits,
    }

    return ('Edit', data)


# Will show you a random page from this project, with this slug
# If project_id == 0, then use all projects
@login_required
@rodan_view(Job)
def task(request, job, project_id=0):
    rodan_user = request.user.get_profile()

    if int(project_id) == 0:
        # Choose a random page!
        all_pages = Page.objects.all()
    else:
        project = get_object_or_404(Project, pk=project_id)
        all_pages = project.page_set.all()

    # Don't allow users to view this for automatic jobs
    if job.get_object().is_automatic:
        raise Http404

    # Now, try to find a page in this project that has this job next
    # (May have been started by the current user but never finished)
    possible_pages = [page for page in all_pages if page.get_next_job(user=rodan_user) == job and page.workflow.has_started]

    # No pages that need this job. Show a 404 for now.
    if not possible_pages:
        raise Http404

    page = random.choice(possible_pages)

    # This is needed in case we're looking at all the projects
    project = page.project

    # Start the job, noting this user (create the result, with no end time)
    # If the job has already been started by this user, do nothing
    page.start_next_job(rodan_user)

    job_object = job.get_object()
    view_data = job.get_view(page)
    data = {
        'disable_breadcrumbs': True,
        'project': project,
        'job': job,
        'page': page,
        'original_image': page.get_latest_thumb_url(size=settings.ORIGINAL_SIZE),
        'large_thumbnail': page.get_latest_thumb_url(size=settings.LARGE_THUMBNAIL),
        'medium_thumbnail': page.get_latest_thumb_url(size=settings.MEDIUM_THUMBNAIL),
        'small_thumbnail': page.get_latest_thumb_url(size=settings.SMALL_THUMBNAIL),
        'job_template': view_data[0],
        'context': view_data[1],
        'form_action': reverse('task_complete', args=[page.id, job.slug]),
        'form': True,
    }

    return (job.name, data)


@login_required
@rodan_view(Project)
def upload(request, project):
    if not project.is_owned_by(request.user):
        raise Http404

    if request.method == 'POST':
        sample_image = request.POST.get('sample', 0)
        if Page.objects.filter(pk=sample_image).count() == 1:
            # Return the workflow edit page
            return redirect('new_workflow', sample_image)
        else:
            # If there's an image specified, create a new workflow for that page
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES['file']
                # Do stuff
                new_page = Page.objects.create(project=project, filename=file.name)
                new_page.handle_image_upload(file)

            # Figure out where to go next
            # Stay on the same page

    form = UploadFileForm()

    data = {
        'project': project,
        'form': form,
        'file_upload': True,
    }

    return ('Upload images', data)


@rodan_view(Project)
def workflows(request, project):
    workflows = Workflow.objects.filter(page__project=project).distinct()
    data = {
        'project': project,
        'workflows': workflows,
    }

    return ('Manage workflows', data)
