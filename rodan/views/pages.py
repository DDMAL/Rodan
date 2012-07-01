from django.http import Http404
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.urlresolvers import reverse

from rodan.models.projects import Page, Job, JobItem
from rodan.models.results import Result
from rodan.utils import rodan_view
from rodan.forms.workflows import WorkflowForm
from rodan.models.jobs import JobType
from rodan.views.projects import task as task_view


@rodan_view(Page)
def view(request, page):
    steps = []

    job_items = page.workflow.jobitem_set.all() if page.workflow else []
    for job_item in job_items:
        try:
            result = Result.objects.get(page=page, job_item=job_item)
            is_done = result.end_total_time is not None
        except Result.DoesNotExist:
            is_done = False

        step = {
            'job': job_item.job,
            'thumbnail': page.get_thumb_url(job=job_item.job, size=settings.SMALL_THUMBNAIL),
            'is_done': is_done,
            'large_thumbnail': page.get_thumb_url(job=job_item.job, size=settings.LARGE_THUMBNAIL),
        }

        steps.append(step)

    user = request.user.get_profile() if request.user.is_authenticated() else None

    data = {
        'next_available_job': page.get_next_job(user=user),
        'medium_thumbnail': page.get_thumb_url(size=settings.MEDIUM_THUMBNAIL),
        'page': page,
        'steps': steps,
    }

    return ('View', data)


@login_required
@rodan_view(Page, Job)
# Called when submiting the form on the task page
def process(request, page, job):
    if request.method != 'POST':
        return task_view(request, job_slug=job.slug, page_id=page.id)
    else:
        job_object = job.get_object()
        kwargs = {}
        parameters = job_object.parameters

        for parameter, default in parameters.iteritems():
            param_type = type(default)
            # The `type` method returns a typecasting function
            # For example, type(1) returns int; int('1') -> 1 (of type int)
            kwargs[parameter] = param_type(request.POST.get(parameter, default))

        # First create a result ...
        job_item = JobItem.objects.get(workflow=page.workflow, job=job)
        result = Result.objects.get(job_item=job_item, user=request.user.get_profile(), page=page)

        # Figure out the relevant task etc
        result.update_end_manual_time()
        job_object.on_post(result.id, **kwargs)

        return redirect(page.project.get_absolute_url() + '?done=1')


def edit_parameters(request, page, job, workflow_jobs):
    template, context = job.get_view(None)

    data = {
        'job': job,
        'workflow_jobs': ' '.join([workflow_job.slug for workflow_job in workflow_jobs]),
        'template': template,
        'context': context,
        'medium_thumbnail': page.get_thumb_url(size=settings.MEDIUM_THUMBNAIL),
        'large_thumbnail': page.get_thumb_url(size=settings.LARGE_THUMBNAIL),
    }
    return render(request, 'pages/edit_parameters.html', data)


@rodan_view(Page)
def workflow(request, page):
    if not page.project.is_owned_by(request.user):
        raise Http404

    if request.method == 'POST':
        form = WorkflowForm(request.POST)
        if form.is_valid():
            new_workflow = form.save(commit=False)
            new_workflow.project = page.project
            new_workflow.save()
            # Set this page's workflow to the newly-created one
            page.workflow = new_workflow
            page.save()
            return redirect('add_jobs', page.id)
    else:
        form = WorkflowForm()

    data = {
        'page': page,
        'form': form,
    }
    return ('New workflow', data)

@login_required
@rodan_view(Page)
def add_jobs(request, page):
    if not page.project.is_owned_by(request.user):
        raise Http404

    if request.method == 'POST':
        done = request.POST.get('done', '')
        if done:
            page.workflow.has_started = True
            page.workflow.save()
            return redirect('add_pages', workflow_id=page.workflow.id)

        job_to_add_slug = request.POST.get('job_to_add', '')
        remove_job = bool(request.POST.get('job_to_remove', ''))

        if job_to_add_slug:
            try:
                job_to_add = Job.objects.get(pk=job_to_add_slug)
                # Add validation later
                sequence = page.workflow.jobs.count() + 1
                job_item = JobItem.objects.create(workflow=page.workflow, job=job_to_add, sequence=sequence)
            except Job.DoesNotExist:
                print "Job does not exist!"

        elif remove_job:
            job_items = JobItem.objects.filter(workflow=page.workflow).order_by('-sequence')
            if job_items.count():
                job_items[0].delete()

    workflow_jobs = [job_item.job for job_item in page.workflow.jobitem_set.all()]
    if workflow_jobs:
        last_job = workflow_jobs[-1]
        available_jobs = [job for job in Job.objects.filter(enabled=True) if job not in workflow_jobs and last_job.is_compatible(job)]
    else:
        # No jobs in the workflow, show all image input jobs
        available_jobs = [job for job in Job.objects.filter(enabled=True) if job.get_object().input_type == JobType.IMAGE]

    data = {
        'available_jobs': available_jobs,
        'workflow_jobs': workflow_jobs,
        'page': page,
        'medium_thumbnail': page.get_thumb_url(settings.MEDIUM_THUMBNAIL),
        'form': True,
    }
    return ('Add jobs', data)


@login_required
@rodan_view(Page, Job)
def restart(request, page, job):
    try:
        this_sequence = page.workflow.jobitem_set.get(job=job).sequence
        # Delete all the results whose jobitems have sequence >= this one
        results_to_delete = page.result_set.filter(job_item__sequence__gte=this_sequence)
        results_to_delete.delete()

        # If the next job is automatic, make it start too
        page.start_next_automatic_job(user=request.user.get_profile())
        # Should show a flash message eventually
    except Page.DoesNotExist:
        print "page does not exist for some reason"

    return redirect(page.get_absolute_url())
