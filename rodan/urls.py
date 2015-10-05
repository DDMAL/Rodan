import os
from django.conf.urls import patterns, include, url, static
from django.conf import settings
from django.contrib import admin

from rest_framework.urlpatterns import format_suffix_patterns

from djoser import views as djoser_views

from rodan.views.auth import AuthMeView, AuthTokenView

from rodan.views.project import ProjectList
from rodan.views.project import ProjectDetail
from rodan.views.workflow import WorkflowList
from rodan.views.workflow import WorkflowDetail
from rodan.views.workflowjob import WorkflowJobList
from rodan.views.workflowjob import WorkflowJobDetail
from rodan.views.workflowjobgroup import WorkflowJobGroupList
from rodan.views.workflowjobgroup import WorkflowJobGroupDetail
from rodan.views.workflowrun import WorkflowRunList
from rodan.views.workflowrun import WorkflowRunDetail
from rodan.views.runjob import RunJobList
from rodan.views.runjob import RunJobDetail
from rodan.views.job import JobList
from rodan.views.job import JobDetail
from rodan.views.user import UserList
from rodan.views.user import UserDetail
from rodan.views.resultspackage import ResultsPackageList, ResultsPackageDetail
from rodan.views.connection import ConnectionList, ConnectionDetail
from rodan.views.outputport import OutputPortList, OutputPortDetail
from rodan.views.outputporttype import OutputPortTypeList, OutputPortTypeDetail
from rodan.views.inputport import InputPortList, InputPortDetail
from rodan.views.inputporttype import InputPortTypeList, InputPortTypeDetail
from rodan.views.resource import ResourceList, ResourceDetail, ResourceViewer
from rodan.views.resourcetype import ResourceTypeList, ResourceTypeDetail
from rodan.views.output import OutputList, OutputDetail
from rodan.views.input import InputList, InputDetail

from rodan.views.workflowjobcoordinateset import WorkflowJobCoordinateSetList
from rodan.views.workflowjobcoordinateset import WorkflowJobCoordinateSetDetail

from rodan.views.taskqueue import TaskQueueActiveView, TaskQueueConfigView, TaskQueueScheduledView, TaskQueueStatusView
from rodan.views.interactive import InteractiveAcquireView, InteractiveWorkingView

# run-once import, initialize Rodan database
import rodan.jobs.load

urlpatterns = []

if settings.DEBUG:
    from rodan.admin.helpers import required, logged_in_or_basicauth
    urlpatterns += required(
        logged_in_or_basicauth('Rodan admin'),
        patterns('',
                 (r'^admin/', include(admin.site.urls))
        )
    )

urlpatterns += format_suffix_patterns(
    patterns('',
             url(r'^$', 'rodan.views.main.api_root'),
             url(r'^taskqueue/active/$', TaskQueueActiveView.as_view(), name="taskqueue-active"),
             #url(r'^taskqueue/config/$', TaskQueueConfigView.as_view(), name="taskqueue-config"),
             url(r'^taskqueue/scheduled/$', TaskQueueScheduledView.as_view(), name="taskqueue-scheduled"),
             url(r'^taskqueue/status/$', TaskQueueStatusView.as_view(), name="taskqueue-status"),
             url(r'^projects/$', ProjectList.as_view(), name="project-list"),
             url(r'^project/(?P<pk>[0-9a-f]{32})/$', ProjectDetail.as_view(), name="project-detail"),
             url(r'^workflows/$', WorkflowList.as_view(), name="workflow-list"),
             url(r'^workflow/(?P<pk>[0-9a-f]{32})/$', WorkflowDetail.as_view(), name="workflow-detail"),
             url(r'^workflowjobs/$', WorkflowJobList.as_view(), name="workflowjob-list"),
             url(r'^workflowjob/(?P<pk>[0-9a-f]{32})/$', WorkflowJobDetail.as_view(), name="workflowjob-detail"),
             url(r'^workflowjobgroups/$', WorkflowJobGroupList.as_view(), name="workflowjobgroup-list"),
             url(r'^workflowjobgroup/(?P<pk>[0-9a-f]{32})/$', WorkflowJobGroupDetail.as_view(), name="workflowjobgroup-detail"),
             url(r'^jobs/$', JobList.as_view(), name="job-list"),
             url(r'^job/(?P<pk>[0-9a-f]{32})/$', JobDetail.as_view(), name="job-detail"),
             url(r'^users/$', UserList.as_view(), name="user-list"),
             url(r'^user/(?P<pk>[0-9\-]+)/$', UserDetail.as_view(), name="user-detail"),
             url(r'^workflowruns/$', WorkflowRunList.as_view(), name="workflowrun-list"),
             url(r'^workflowrun/(?P<pk>[0-9a-f]{32})/$', WorkflowRunDetail.as_view(), name="workflowrun-detail"),
             url(r'^runjobs/$', RunJobList.as_view(), name="runjob-list"),
             url(r'^runjob/(?P<pk>[0-9a-f]{32})/$', RunJobDetail.as_view(), name="runjob-detail"),
             url(r'^resultspackages/$', ResultsPackageList.as_view(), name="resultspackage-list"),
             url(r'^resultspackage/(?P<pk>[0-9a-f]{32})/$', ResultsPackageDetail.as_view(), name="resultspackage-detail"),
             url(r'^connections/$', ConnectionList.as_view(), name="connection-list"),
             url(r'^connection/(?P<pk>[0-9a-f]{32})/$', ConnectionDetail.as_view(), name="connection-detail"),
             url(r'^outputporttypes/$', OutputPortTypeList.as_view(), name="outputporttype-list"),
             url(r'^outputporttype/(?P<pk>[0-9a-f]{32})/$', OutputPortTypeDetail.as_view(), name="outputporttype-detail"),
             url(r'^outputports/$', OutputPortList.as_view(), name="outputport-list"),
             url(r'^outputport/(?P<pk>[0-9a-f]{32})/$', OutputPortDetail.as_view(), name="outputport-detail"),
             url(r'^inputporttypes/$', InputPortTypeList.as_view(), name="inputporttype-list"),
             url(r'^inputporttype/(?P<pk>[0-9a-f]{32})/$', InputPortTypeDetail.as_view(), name="inputporttype-detail"),
             url(r'^inputports/$', InputPortList.as_view(), name="inputport-list"),
             url(r'^inputport/(?P<pk>[0-9a-f]{32})/$', InputPortDetail.as_view(), name="inputport-detail"),
             url(r'^resources/$', ResourceList.as_view(), name="resource-list"),
             url(r'^resource/(?P<pk>[0-9a-f]{32})/$', ResourceDetail.as_view(), name="resource-detail"),
             url(r'^resource/(?P<pk>[0-9a-f]{32})/viewer/$', ResourceViewer.as_view(), name="resource-viewer"),
             url(r'^resourcetypes/$', ResourceTypeList.as_view(), name="resourcetype-list"),
             url(r'^resourcetype/(?P<pk>[0-9a-f]{32})/$', ResourceTypeDetail.as_view(), name="resourcetype-detail"),
             url(r'^outputs/$', OutputList.as_view(), name="output-list"),
             url(r'^output/(?P<pk>[0-9a-f]{32})/$', OutputDetail.as_view(), name="output-detail"),
             url(r'^inputs/$', InputList.as_view(), name="input-list"),
             url(r'^input/(?P<pk>[0-9a-f]{32})/$', InputDetail.as_view(), name='input-detail'),
             url(r'^interactive/(?P<run_job_uuid>[0-9a-f]{32})/acquire/$', InteractiveAcquireView.as_view(), name='interactive-acquire'),
             url(r'^interactive/(?P<run_job_uuid>[0-9a-f]{32})/(?P<working_user_token>[0-9a-f]{32})/(?P<additional_url>.*)$', InteractiveWorkingView.as_view(), name='interactive-working'),

             url(r'^workflowjobcoordinatesets/$', WorkflowJobCoordinateSetList.as_view(), name="workflowjobcoordinateset-list"),
             url(r'^workflowjobcoordinateset/(?P<pk>[0-9a-f]{32})/$', WorkflowJobCoordinateSetDetail.as_view(), name="workflowjobcoordinateset-detail"),
             url(r'^auth/me/', AuthMeView.as_view(), name="auth-me"),
             url(r'^auth/register/', djoser_views.RegistrationView.as_view(), name="auth-register"),
             url(r'^auth/token/', AuthTokenView.as_view(), name="auth-token"),
             url(r'^auth/reset-token/', djoser_views.LogoutView.as_view(), name="auth-reset-token"),
             url(r'^auth/change-password/', djoser_views.SetPasswordView.as_view(), name="auth-change-password"),
         )
)

# For serving stuff in debug mode only
if settings.DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
