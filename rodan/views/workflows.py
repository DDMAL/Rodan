from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from rodan.utils import rodan_view
from rodan.models.projects import Workflow, Project, Page

@rodan_view(Workflow)
def view(request, workflow):
    data = {}
    return ('View workflow', data)

@rodan_view(Workflow)
def edit(request, workflow):
    data = {}
    return ('View workflow', data)

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
