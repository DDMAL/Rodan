from django.conf.urls import patterns, include, url


urlpatterns = patterns('projects.views',
    url(r'^dashboard', 'dashboard', name='dashboard'),
    url(r'^settings', 'settings'),
    url(r'^(?P<project_id>\d+)/edit', 'edit'),
    url(r'^(?P<project_id>\d+)', 'view'),
    url(r'^page/(?P<page_id>\d+)', 'page_view'),
    url(r'^create', 'create'),
    url(r'^job/create', 'job_create'),
    url(r'^job/(?P<job_id>\d+)/edit', 'job_edit'),
    url(r'^job/(?P<job_id>\d+)', 'job_view'),
    url(r'^workflow/create', 'workflow_create'),
    url(r'^workflow/(?P<workflow_id>\d+)/edit', 'workflow_edit'),
    url(r'^workflow/(?P<workflow_id>\d+)', 'workflow_view'),
)
