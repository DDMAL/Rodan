import os

from django.urls import include, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from decorator_include import decorator_include
from djoser import views as djoser_views
from rest_framework.urlpatterns import format_suffix_patterns

from rodan.admin.helpers import logged_in_or_basicauth
from rodan.views.auth import AuthMeView, AuthTokenView
from rodan.views.project import ProjectList
from rodan.views.project import ProjectDetail, ProjectDetailAdmins, ProjectDetailWorkers
from rodan.views.workflow import WorkflowList, WorkflowDetail, WorkflowResourceAssignments
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
from rodan.views.userpreference import UserPreferenceList, UserPreferenceDetail
from rodan.views.resultspackage import ResultsPackageList, ResultsPackageDetail
from rodan.views.connection import ConnectionList, ConnectionDetail
from rodan.views.outputport import OutputPortList, OutputPortDetail
from rodan.views.outputporttype import OutputPortTypeList, OutputPortTypeDetail
from rodan.views.inputport import InputPortList, InputPortDetail
from rodan.views.inputporttype import InputPortTypeList, InputPortTypeDetail
from rodan.views.resource import (
    ResourceList,
    ResourceDetail,
    ResourceViewer,
    ResourceAcquireView,
    ResourceArchive,
)
from rodan.views.resourcelabel import ResourceLabelList, ResourceLabelDetail
from rodan.views.resourcelist import ResourceListList, ResourceListDetail
from rodan.views.resourcetype import ResourceTypeList, ResourceTypeDetail
from rodan.views.output import OutputList, OutputDetail
from rodan.views.input import InputList, InputDetail
from rodan.views.taskqueue import (
    TaskQueueActiveView,
    TaskQueueScheduledView,
    TaskQueueStatusView,
)
from rodan.views.interactive import InteractiveAcquireView, InteractiveWorkingView
from rodan.views.main import APIRoot, EmptyView

# run-once import, initialize Rodan database
if os.environ.get("TRAVIS", "False") != "true" and os.environ.get("GITHUB_ACTIONS", "False") != "true" and os.environ.get("MIGRATE", "False") == "False":
    import rodan.jobs.load  # noqa

# Admin URL pattern.
# [INFO] - Notice that the Admin URL is specified in the settings.py file,
# as an environment variable.
urlpatterns = [
    re_path(
        settings.ADMIN_URL,
        decorator_include(
            logged_in_or_basicauth("Rodan admin"), admin.site.urls
        ),
    )
]

api_patterns = [
    re_path(r"^$", EmptyView.as_view()),
    re_path(r"^api/$", APIRoot.as_view()),
    re_path(
        r"^api/taskqueue/active/$",
        TaskQueueActiveView.as_view(),
        name="taskqueue-active",
    ),
    # re_path(r'^taskqueue/config/$', TaskQueueConfigView.as_view(), name="taskqueue-config"),
    re_path(
        r"^api/taskqueue/scheduled/$",
        TaskQueueScheduledView.as_view(),
        name="taskqueue-scheduled",
    ),
    re_path(
        r"^api/taskqueue/status/$",
        TaskQueueStatusView.as_view(),
        name="taskqueue-status",
    ),
    re_path(r"^api/projects/$", ProjectList.as_view(), name="project-list"),
    re_path(
        r"^api/project/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        ProjectDetail.as_view(),
        name="project-detail",
    ),
    re_path(
        r"^api/project/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/admins/$",  # noqa
        ProjectDetailAdmins.as_view(),
        name="project-detail-admins",
    ),
    re_path(
        r"^api/project/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/workers/$",  # noqa
        ProjectDetailWorkers.as_view(),
        name="project-detail-workers",
    ),
    re_path(r"^api/workflows/$", WorkflowList.as_view(), name="workflow-list"),
    re_path(
        r"^api/workflow/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        WorkflowDetail.as_view(),
        name="workflow-detail",
    ),
    re_path(
        r"^api/workflow/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/resourceassignments/$",
        WorkflowResourceAssignments.as_view(),
        name="workflow-detail-resourceassignments",
    ),
    re_path(r"^api/workflowjobs/$", WorkflowJobList.as_view(), name="workflowjob-list"),
    re_path(
        r"^api/workflowjob/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        WorkflowJobDetail.as_view(),
        name="workflowjob-detail",
    ),
    re_path(
        r"^api/workflowjobgroups/$",
        WorkflowJobGroupList.as_view(),
        name="workflowjobgroup-list",
    ),
    re_path(
        r"^api/workflowjobgroup/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",  # noqa
        WorkflowJobGroupDetail.as_view(),
        name="workflowjobgroup-detail",
    ),
    re_path(r"^api/jobs/$", JobList.as_view(), name="job-list"),
    re_path(
        r"^api/job/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        JobDetail.as_view(),
        name="job-detail",
    ),
    re_path(r"^api/users/$", UserList.as_view(), name="user-list"),
    re_path(r"^api/user/(?P<pk>[0-9\-]+)/$", UserDetail.as_view(), name="user-detail"),
    re_path(
        r"^api/userpreferences/$",
        UserPreferenceList.as_view(),
        name="userpreference-list",
    ),
    re_path(
        r"^api/userpreference/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",  # noqa
        UserPreferenceDetail.as_view(),
        name="userpreference-detail",
    ),
    re_path(r"^api/workflowruns/$", WorkflowRunList.as_view(), name="workflowrun-list"),
    re_path(
        r"^api/workflowrun/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        WorkflowRunDetail.as_view(),
        name="workflowrun-detail",
    ),
    re_path(r"^api/runjobs/$", RunJobList.as_view(), name="runjob-list"),
    re_path(
        r"^api/runjob/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        RunJobDetail.as_view(),
        name="runjob-detail",
    ),
    re_path(
        r"^api/resultspackages/$",
        ResultsPackageList.as_view(),
        name="resultspackage-list",
    ),
    re_path(
        r"^api/resultspackage/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",  # noqa
        ResultsPackageDetail.as_view(),
        name="resultspackage-detail",
    ),
    re_path(r"^api/connections/$", ConnectionList.as_view(), name="connection-list"),
    re_path(
        r"^api/connection/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        ConnectionDetail.as_view(),
        name="connection-detail",
    ),
    re_path(
        r"^api/outputporttypes/$",
        OutputPortTypeList.as_view(),
        name="outputporttype-list",
    ),
    re_path(
        r"^api/outputporttype/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",  # noqa
        OutputPortTypeDetail.as_view(),
        name="outputporttype-detail",
    ),
    re_path(r"^api/outputports/$", OutputPortList.as_view(), name="outputport-list"),
    re_path(
        r"^api/outputport/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        OutputPortDetail.as_view(),
        name="outputport-detail",
    ),
    re_path(
        r"^api/inputporttypes/$", InputPortTypeList.as_view(), name="inputporttype-list"
    ),
    re_path(
        r"^api/inputporttype/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",  # noqa
        InputPortTypeDetail.as_view(),
        name="inputporttype-detail",
    ),
    re_path(r"^api/inputports/$", InputPortList.as_view(), name="inputport-list"),
    re_path(
        r"^api/inputport/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        InputPortDetail.as_view(),
        name="inputport-detail",
    ),
    re_path(r"^api/resources/$", ResourceList.as_view(), name="resource-list"),
    re_path(
        r"^api/resources/archive/$", ResourceArchive.as_view(), name="resource-archive"
    ),
    re_path(
        r"^api/resource/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        ResourceDetail.as_view(),
        name="resource-detail",
    ),
    re_path(
        r"^api/resource/(?P<resource_uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/(?P<working_user_token>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",  # noqa
        ResourceViewer.as_view(),
        name="resource-viewer",
    ),
    re_path(
        r"^api/resource/(?P<resource_uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/acquire/$",  # noqa
        ResourceAcquireView.as_view(),
        name="resource-viewer-acquire",
    ),
    re_path(r"^api/labels/$", ResourceLabelList.as_view(), name="resourcelabel-list"),
    re_path(
        r"^api/label/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        ResourceLabelDetail.as_view(),
        name="resourcelabel-detail",
    ),
    re_path(r"^api/resourcelists/$", ResourceListList.as_view(), name="resourcelist-list"),
    re_path(
        r"^api/resourcelist/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        ResourceListDetail.as_view(),
        name="resourcelist-detail",
    ),
    re_path(r"^api/resourcetypes/$", ResourceTypeList.as_view(), name="resourcetype-list"),
    re_path(
        r"^api/resourcetype/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        ResourceTypeDetail.as_view(),
        name="resourcetype-detail",
    ),
    re_path(r"^api/outputs/$", OutputList.as_view(), name="output-list"),
    re_path(
        r"^api/output/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        OutputDetail.as_view(),
        name="output-detail",
    ),
    re_path(r"^api/inputs/$", InputList.as_view(), name="input-list"),
    re_path(
        r"^api/input/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        InputDetail.as_view(),
        name="input-detail",
    ),
    re_path(
        r"^api/interactive/(?P<run_job_uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/acquire/$",  # noqa
        InteractiveAcquireView.as_view(),
        name="interactive-acquire",
    ),
    re_path(
        r"^api/interactive/(?P<run_job_uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/(?P<working_user_token>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/(?P<additional_url>.*)$",  # noqa
        InteractiveWorkingView.as_view(),
        name="interactive-working",
    ),
    re_path(r"^api/auth/me/", AuthMeView.as_view(), name="auth-me"),
    re_path(
        r"^api/auth/register/",
        djoser_views.UserViewSet.as_view({'post': 'create'}), #DEPRECATED
        name="auth-register",
    ),
    re_path(
        r"^api/auth/activate/$",
        djoser_views.UserViewSet.as_view({'post': 'activation'}),
        name="auth-activate",
    ),
    re_path(
        r"^api/auth/resend-activation/$", 
    djoser_views.UserViewSet.as_view({'post': 'resend_activation'}), 
        name="auth-resend-activation"
    ),
    re_path(r"^api/auth/token/", AuthTokenView.as_view(), name="auth-token"),
    re_path(
        r"^api/auth/reset-token/",
        djoser_views.TokenDestroyView.as_view(),
        name="auth-reset-token",
    ),
    re_path(
        r"^api/auth/change-password/",
        djoser_views.UserViewSet.as_view({'post': 'set_password'}),
        name="auth-change-password",
    ),
    re_path(
        r"^api/auth/reset-password/$",
        djoser_views.UserViewSet.as_view({'post': 'reset_password'}),
        name="auth-reset-password",
    ),
    re_path(
        r"^api/auth/reset-password/confirm/$",
        djoser_views.UserViewSet.as_view({'post': 'reset_password_confirm'}),
        name="auth-reset-password-confirm",
    ),
    re_path(r"^api/ht/", include("health_check.urls")),
]

urlpatterns += format_suffix_patterns(api_patterns, allowed=["json", "html"])

# For serving stuff in debug mode only
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
