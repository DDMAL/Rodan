from rodan.models.projects import Project
from django.core.urlresolvers import reverse

def list_projects(request):
    return {
        'projects': Project.objects.all()
    }

def login_url(request):
    return {
        'login_url': reverse('signup') + '?next=' + request.get_full_path()
    }
