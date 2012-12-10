from django.conf.urls import patterns, include, url, static
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token

from rodan.views.auth import session_auth
from rodan.views.auth import session_status

from rodan.views.main import ProjectList
from rodan.views.main import ProjectDetail
from rodan.views.main import WorkflowList
from rodan.views.main import WorkflowDetail
from rodan.views.main import WorkflowJobList
from rodan.views.main import WorkflowJobDetail
from rodan.views.main import PageList
from rodan.views.main import PageDetail
from rodan.views.main import JobList
from rodan.views.main import JobDetail
from rodan.views.main import ResultList
from rodan.views.main import ResultDetail
from rodan.views.main import UserList
from rodan.views.main import UserDetail

urlpatterns = []

urlpatterns += format_suffix_patterns(
    patterns('rodan.views.main',
        url(r'^browse/$', 'api_root'),
        url(r'^auth/token/$', obtain_auth_token),
        url(r'^auth/session/$', session_auth),
        url(r'^auth/status/$', session_status),
        url(r'^$', 'home'),
        url(r'^projects/$', ProjectList.as_view(), name="project-list"),
        url(r'^project/(?P<pk>[0-9]+)/$', ProjectDetail.as_view(), name="project-detail"),
        url(r'^workflows/$', WorkflowList.as_view(), name="workflow-list"),
        url(r'^workflow/(?P<pk>[0-9]+)/$', WorkflowDetail.as_view(), name="workflow-detail"),
        url(r'^workflowjobs/$', WorkflowJobList.as_view(), name="workflowjob-list"),
        url(r'^workflowjob/(?P<pk>[0-9]+)/$', WorkflowJobDetail.as_view(), name="workflowjob-detail"),
        url(r'^pages/$', PageList.as_view(), name="page-list"),
        url(r'^page/(?P<pk>[0-9]+)/$', PageDetail.as_view(), name="page-detail"),
        url(r'^jobs/$', JobList.as_view(), name="job-list"),
        url(r'^job/(?P<pk>[0-9]+)/$', JobDetail.as_view(), name="job-detail"),
        url(r'^results/$', ResultList.as_view(), name="result-list"),
        url(r'^result/(?P<pk>[0-9]+)/$', ResultDetail.as_view(), name="result-detail"),
        url(r'^users/$', UserList.as_view(), name="user-list"),
        url(r'^user/(?P<pk>[0-9]+)/$', UserDetail.as_view(), name="user-detail"),
    )
)

urlpatterns += patterns('',
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework'))
)


# Only add admin if it's enabled
if 'django.contrib.admin' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^admin/', include(admin.site.urls)),
    )

# For serving stuff under MEDIA_ROOT in debug mode only
if settings.DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
