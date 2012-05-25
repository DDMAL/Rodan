from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^dashboard', 'projects.views.dashboard'),
    url(r'^settings', 'projects.views.settings'),
    url(r'^(?P<project_id>\d+)', 'projects.views.view'),
    url(r'^page/(?P<page_id>\d+)', 'projects.views.page_view'),
    url(r'^create', 'projects.views.create'),
)
