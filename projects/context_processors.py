from projects.models import * 

def list_projects(request):

    return {
        'projects': Project.objects.all()
    }
