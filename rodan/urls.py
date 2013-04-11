from django.conf.urls import patterns, include, url, static
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token

from rodan.views.auth import session_auth
from rodan.views.auth import session_status

# from rodan.views.upload import page_upload

from rodan.views.project import ProjectList
from rodan.views.project import ProjectDetail
from rodan.views.workflow import WorkflowList
from rodan.views.workflow import WorkflowDetail
from rodan.views.workflowjob import WorkflowJobList
from rodan.views.workflowjob import WorkflowJobDetail
from rodan.views.workflowrun import WorkflowRunList
from rodan.views.workflowrun import WorkflowRunDetail
from rodan.views.runjob import RunJobList
from rodan.views.runjob import RunJobDetail
from rodan.views.page import PageList
from rodan.views.page import PageDetail
from rodan.views.job import JobList
from rodan.views.job import JobDetail
from rodan.views.result import ResultList
from rodan.views.result import ResultDetail
from rodan.views.user import UserList
from rodan.views.user import UserDetail

urlpatterns = []

urlpatterns += format_suffix_patterns(
    patterns('rodan.views.main',
        url(r'^browse/$', 'api_root'),
        url(r'^auth/token/$', obtain_auth_token),
        url(r'^auth/session/$', session_auth),
        url(r'^auth/status/$', session_status),
        url(r'^$', 'home'),
        url(r'^projects/$', ProjectList.as_view(), name="project-list"),
        url(r'^project/(?P<pk>[0-9a-z\-]+)/$', ProjectDetail.as_view(), name="project-detail"),
        url(r'^workflows/$', WorkflowList.as_view(), name="workflow-list"),
        url(r'^workflow/(?P<pk>[0-9a-z\-]+)/$', WorkflowDetail.as_view(), name="workflow-detail"),
        url(r'^workflowjobs/$', WorkflowJobList.as_view(), name="workflowjob-list"),
        url(r'^workflowjob/(?P<pk>[0-9a-z\-]+)/$', WorkflowJobDetail.as_view(), name="workflowjob-detail"),
        url(r'^pages/$', PageList.as_view(), name="page-list"),
        url(r'^page/(?P<pk>[0-9a-z\-]+)/$', PageDetail.as_view(), name="page-detail"),
        url(r'^jobs/$', JobList.as_view(), name="job-list"),
        url(r'^job/(?P<pk>[0-9a-z\-]+)/$', JobDetail.as_view(), name="job-detail"),
        url(r'^results/$', ResultList.as_view(), name="result-list"),
        url(r'^result/(?P<pk>[0-9a-z\-]+)/$', ResultDetail.as_view(), name="result-detail"),
        url(r'^users/$', UserList.as_view(), name="user-list"),
        url(r'^user/(?P<pk>[0-9]+)/$', UserDetail.as_view(), name="user-detail"),
        url(r'^workflowruns/$', WorkflowRunList.as_view(), name="workflowrun-list"),
        url(r'^workflowrun/(?P<pk>[0-9a-z\-]+)/$', WorkflowRunDetail.as_view(), name="workflowrun-detail"),
        url(r'^runjobs/$', RunJobList.as_view(), name="runjob-list"),
        url(r'^runjob/(?P<pk>[0-9a-z\-]+)/$', RunJobDetail.as_view(), name="runjob-detail"),
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
