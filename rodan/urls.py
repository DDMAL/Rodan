from django.conf.urls import patterns, include, url, static
from django.conf import settings
from django.contrib import admin

from rodan.jobs.neon import neon_urls

admin.autodiscover()

project_urls = patterns('rodan.views.projects',
    url(r'^/?$', 'view', name='view_project'),
    url(r'^/edit', 'edit', name='edit_project'),
    url(r'^/upload', 'upload', name='upload'),
    url(r'^/workflows', 'workflows', name='manage_workflows'),
    url(r'^/diva$', 'diva', name='diva'),
    url(r'^/divaserve', 'divaserve'),
    url(r'^/query', 'query'),
    url(r'^/(?P<job_slug>[^/]+)', 'task', name="project_task"),
)

workflow_urls = patterns('rodan.views.workflows',
    url(r'^/?$', 'view'),
    url(r'^/edit', 'edit', name='edit_workflow'),
    url(r'^/add', 'add_pages', name='add_pages'),
    url(r'^/jobs', 'manage_jobs', name='workflow_jobs'),
)

page_urls = patterns('rodan.views.pages',
    url(r'^/?$', 'view', name='view_page'),
    url(r'^/jobs', 'add_jobs', name='add_jobs'),
    url(r'^/workflow', 'workflow', name='new_workflow'),
    url(r'^/restart/(?P<job_slug>[^/]+)', 'restart', name='restart_job'),
    url(r'^/set', 'set_workflow', name='set_workflow'),
    url(r'^/clone', 'clone_workflow', name='clone_workflow'),
    url(r'^/(?P<job_slug>[^/]+)', 'process', name='task_complete'),
)

urlpatterns = []
# Only add admin if it's enabled
if 'django.contrib.admin' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^admin/', include(admin.site.urls)),
    )

urlpatterns += patterns('rodan.views.main',
    url(r'^$', 'home', name='home'),
    url(r'^signup', 'signup', name='signup'),
    url(r'^logout', 'logout_view', name='logout'),
)

urlpatterns += patterns('rodan.views.projects',
    url(r'^dashboard', 'dashboard', name='dashboard'),
    url(r'^create', 'create', name='create_project'),
    url(r'^projects/(?P<project_id>\d+)', include(project_urls)),
)

urlpatterns += patterns('rodan.views.workflows',
    url(r'^workflows/(?P<workflow_id>\d+)', include(workflow_urls)),
)

urlpatterns += patterns('rodan.views.jobs',
    url(r'^jobs/(?P<job_slug>[^/]+)', 'view'),
)

urlpatterns += patterns('rodan.views.pages',
    url(r'^pages/(?P<page_id>\d+)', include(page_urls)),
)

urlpatterns += patterns('',
    url(r'^neon/edit/(?P<page_id>\d+)/', include(neon_urls)),
)

urlpatterns += patterns('rodan.views.status',
    url(r'^status/task', 'task'),
    url(r'^status/page/(?P<page_id>\d+)', 'page'),
)

# For serving stuff under MEDIA_ROOT in debug mode only
if settings.DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
