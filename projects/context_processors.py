def list_projects(request):
    # Fake list of projects for now
    projects = []

    for i in xrange(1, 41):
        this_project = {
            'name': 'Project %d' % i,
            'desc': 'Some random description',
            'id': i,
        }
        projects.append(this_project)

    return {
        'projects': projects
    }
