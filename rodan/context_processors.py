from django.core.urlresolvers import reverse
from rodan.models.project import Project


def list_projects(request):
    return {
        'project_list': Project.objects.order_by('-id').all()
    }


def login_url(request):
    return {
        'login_url': reverse('signup') + '?next=' + request.get_full_path()
    }
