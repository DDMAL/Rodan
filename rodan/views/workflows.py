import random

from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from rodan.utils import rodan_view, chunkify
from rodan.models.projects import Workflow, Project, Page
from rodan.forms.workflows import WorkflowForm


@rodan_view(Workflow)
def view(request, workflow):
    pages = workflow.page_set.all()
    num_per_row = 4

    data = {
        'user_can_edit': workflow.project.is_owned_by(request.user),
        'pages': pages,
        'total_progress': workflow.get_percent_done(),
        'job_items': workflow.jobitem_set.all(),
        'page_sections': list(chunkify(pages, num_per_row)),
        'num_per_row': num_per_row,
        'num_to_fill': num_per_row - (len(pages) % num_per_row),
    }

    return ('View workflow', data)


@rodan_view(Workflow)
def edit(request, workflow):
    if not workflow.project.is_owned_by(request.user):
        raise Http404

    if request.method == 'POST':
        form = WorkflowForm(request.POST, instance=workflow)

        if form.is_valid():
            workflow = form.save()
            return redirect(workflow)
    else:
        form = WorkflowForm(instance=workflow)

    data = {
        'form': form
    }
    return ('Edit workflow', data)


@login_required
@rodan_view(Workflow)
def add_pages(request, workflow):
    project = Project.objects.filter(page__workflow=workflow).distinct()[0]

    if project.is_owned_by(request.user):
        if request.method == 'POST':
            page_ids = request.POST.getlist('page')
            try:
                for page_id in page_ids:
                    page = Page.objects.get(pk=page_id)
                    page.workflow = workflow
                    page.save()

                for page in workflow.page_set.all():
                    page.start_next_automatic_job(request.user.get_profile())

                return redirect('view_project', project_id=project.id)
            except Page.DoesNotExist:
                print "Specified an invalid page ID oh no!!!"

        data = {
            'workflow': workflow,
            'project': project,
            'form': True
        }
        return ('Add pages to workflow', data)
    else:
        raise Http404


def manage_jobs(request, workflow_id):
    # Choose a sample page at random for now
    workflow = Workflow.objects.get(pk=workflow_id)
    pages = workflow.project.page_set.all()

    if pages.count():
        random_page = random.choice(pages)
        return redirect('add_jobs', page_id=random_page.id)
    else:
        raise Http404
