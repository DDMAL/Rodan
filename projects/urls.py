from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^dashboard', 'projects.views.dashboard'),
    url(r'^settings', 'projects.views.settings'),
    url(r'^(?P<project_id>\d+)/edit', 'projects.views.edit'),
    url(r'^(?P<project_id>\d+)', 'projects.views.view'),
    url(r'^page/(?P<page_id>\d+)', 'projects.views.page_view'),
    url(r'^create', 'projects.views.create'),
    url(r'^job/create', 'projects.views.job_create'),
    url(r'^job/(?P<job_id>\d+)', 'projects.views.job_edit'),
    url(r'^workflow/create', 'projects.views.workflow_create'),
    url(r'^workflow/(?P<workflow_id>\d+)', 'projects.views.workflow_edit'),
)
