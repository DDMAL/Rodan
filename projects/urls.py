from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^dashboard', 'projects.views.dashboard'),
    url(r'^settings', 'projects.views.settings'),
    url(r'^view/(?P<project_id>\d+)', 'projects.views.view'),
)
