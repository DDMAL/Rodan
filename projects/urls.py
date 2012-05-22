from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^dashboard', 'projects.views.dashboard'),
    url(r'^create', 'projects.views.create'),
    url(r'^settings', 'projects.views.settings'),
)
