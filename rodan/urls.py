from django.conf.urls import patterns, include, url, static
from django.conf import settings

project_urls = patterns('rodan.views.projects',
    url(r'^/?$', 'view'),
    url(r'^/edit', 'edit', name='edit_project'),
    url(r'^/add', 'add_pages', name='add_pages'),
    url(r'^/(?P<job_slug>[^/]+)', 'task', name="project_task"),
)

urlpatterns = patterns('rodan.views.main',
    url(r'^$', 'home', name='home'),
    url(r'^signup', 'signup', name='signup'),
    url(r'^logout', 'logout_view', name='logout'),
    url(r'^settings', 'settings', name='settings'),
)

urlpatterns += patterns('rodan.views.projects',
    url(r'^dashboard', 'dashboard', name='dashboard'),
    url(r'^create', 'create', name='create_project'),
    url(r'^projects/(?P<project_id>\d+)', include(project_urls)),
)

urlpatterns += patterns('rodan.views.workflows',
    url(r'^workflows/(?P<workflow_id>\d+)', 'view'),
)

urlpatterns += patterns('rodan.views.jobs',
    url(r'^jobs/(?P<job_slug>[^/]+)', 'view'),
)

urlpatterns += patterns('rodan.views.pages',
    url(r'^pages/(?P<page_id>\d+)/(?P<job_slug>[^/]+)', 'process', name='task_complete'),
    url(r'^pages/(?P<page_id>\d+)', 'view'),
)

# For serving stuff under MEDIA_ROOT in debug mode only
if settings.DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
