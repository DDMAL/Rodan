import os

from django.conf.urls import (
    include,
    url,
    static
)
from django.conf import settings
from django.contrib import admin
from decorator_include import decorator_include
from djoser import views as djoser_views
from rest_framework.urlpatterns import format_suffix_patterns

from rodan.admin.helpers import logged_in_or_basicauth
from rodan.views.auth import AuthMeView, AuthTokenView
from rodan.views.project import ProjectList
from rodan.views.project import (
    ProjectDetail,
    ProjectDetailAdmins,
    ProjectDetailWorkers
)
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
)
from rodan.views.resourcelabel import ResourceLabelList, ResourceLabelDetail
from rodan.views.resourcelist import ResourceListList, ResourceListDetail
from rodan.views.resourcetype import ResourceTypeList, ResourceTypeDetail
from rodan.views.output import OutputList, OutputDetail
from rodan.views.input import InputList, InputDetail
from rodan.views.workflowjobcoordinateset import WorkflowJobCoordinateSetList
from rodan.views.workflowjobcoordinateset import WorkflowJobCoordinateSetDetail
from rodan.views.workflowjobgroupcoordinateset import WorkflowJobGroupCoordinateSetList
from rodan.views.workflowjobgroupcoordinateset import (
    WorkflowJobGroupCoordinateSetDetail
)
from rodan.views.taskqueue import (
    TaskQueueActiveView,
    TaskQueueScheduledView,
    TaskQueueStatusView,
)
from rodan.views.interactive import (
    InteractiveAcquireView,
    InteractiveWorkingView
)
from rodan.views.main import APIRoot, EmptyView

# run-once import, initialize Rodan database
if os.environ.get("TRAVIS", "False") != "true":
    import rodan.jobs.load  # noqa

# Admin URL pattern.
# [INFO] - Notice that the Admin URL is specified in the settings.py file,
# as an environment variable.
urlpatterns = [
    url(
        settings.ADMIN_URL,
        decorator_include(
            logged_in_or_basicauth("Rodan admin"),
            include(admin.site.urls)
        )
    )
]

api_patterns = [
    url(r"^$", EmptyView.as_view()),
    url(r"^api/$", APIRoot.as_view()),
    url(
        r"^api/taskqueue/active/$",
        TaskQueueActiveView.as_view(),
        name="taskqueue-active",
    ),
    # url(r'^taskqueue/config/$', TaskQueueConfigView.as_view(), name="taskqueue-config"),
    url(
        r"^api/taskqueue/scheduled/$",
        TaskQueueScheduledView.as_view(),
        name="taskqueue-scheduled",
    ),
    url(
        r"^api/taskqueue/status/$",
        TaskQueueStatusView.as_view(),
        name="taskqueue-status",
    ),
    url(r"^api/projects/$", ProjectList.as_view(), name="project-list"),
    url(
        r"^api/project/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        ProjectDetail.as_view(),
        name="project-detail",
    ),
    url(
        r"^api/project/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/admins/$",  # noqa
        ProjectDetailAdmins.as_view(),
        name="project-detail-admins",
    ),
    url(
        r"^api/project/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/workers/$",  # noqa
        ProjectDetailWorkers.as_view(),
        name="project-detail-workers",
    ),
    url(r"^api/workflows/$", WorkflowList.as_view(), name="workflow-list"),
    url(
        r"^api/workflow/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        WorkflowDetail.as_view(),
        name="workflow-detail",
    ),
    url(r"^api/workflowjobs/$", WorkflowJobList.as_view(), name="workflowjob-list"),
    url(
        r"^api/workflowjob/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        WorkflowJobDetail.as_view(),
        name="workflowjob-detail",
    ),
    url(
        r"^api/workflowjobgroups/$",
        WorkflowJobGroupList.as_view(),
        name="workflowjobgroup-list",
    ),
    url(
        r"^api/workflowjobgroup/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",  # noqa
        WorkflowJobGroupDetail.as_view(),
        name="workflowjobgroup-detail",
    ),
    url(r"^api/jobs/$", JobList.as_view(), name="job-list"),
    url(
        r"^api/job/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        JobDetail.as_view(),
        name="job-detail",
    ),
    url(r"^api/users/$", UserList.as_view(), name="user-list"),
    url(r"^api/user/(?P<pk>[0-9\-]+)/$", UserDetail.as_view(), name="user-detail"),
    url(
        r"^api/userpreferences/$",
        UserPreferenceList.as_view(),
        name="userpreference-list",
    ),
    url(
        r"^api/userpreference/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",  # noqa
        UserPreferenceDetail.as_view(),
        name="userpreference-detail",
    ),
    url(r"^api/workflowruns/$", WorkflowRunList.as_view(), name="workflowrun-list"),
    url(
        r"^api/workflowrun/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        WorkflowRunDetail.as_view(),
        name="workflowrun-detail",
    ),
    url(r"^api/runjobs/$", RunJobList.as_view(), name="runjob-list"),
    url(
        r"^api/runjob/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        RunJobDetail.as_view(),
        name="runjob-detail",
    ),
    url(
        r"^api/resultspackages/$",
        ResultsPackageList.as_view(),
        name="resultspackage-list",
    ),
    url(
        r"^api/resultspackage/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",  # noqa
        ResultsPackageDetail.as_view(),
        name="resultspackage-detail",
    ),
    url(r"^api/connections/$", ConnectionList.as_view(), name="connection-list"),
    url(
        r"^api/connection/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        ConnectionDetail.as_view(),
        name="connection-detail",
    ),
    url(
        r"^api/outputporttypes/$",
        OutputPortTypeList.as_view(),
        name="outputporttype-list",
    ),
    url(
        r"^api/outputporttype/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",  # noqa
        OutputPortTypeDetail.as_view(),
        name="outputporttype-detail",
    ),
    url(r"^api/outputports/$", OutputPortList.as_view(), name="outputport-list"),
    url(
        r"^api/outputport/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        OutputPortDetail.as_view(),
        name="outputport-detail",
    ),
    url(
        r"^api/inputporttypes/$", InputPortTypeList.as_view(), name="inputporttype-list"
    ),
    url(
        r"^api/inputporttype/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",  # noqa
        InputPortTypeDetail.as_view(),
        name="inputporttype-detail",
    ),
    url(r"^api/inputports/$", InputPortList.as_view(), name="inputport-list"),
    url(
        r"^api/inputport/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        InputPortDetail.as_view(),
        name="inputport-detail",
    ),
    url(r"^api/resources/$", ResourceList.as_view(), name="resource-list"),
    url(
        r"^api/resource/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        ResourceDetail.as_view(),
        name="resource-detail",
    ),
    url(
        r"^api/resource/(?P<resource_uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/(?P<working_user_token>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",  # noqa
        ResourceViewer.as_view(),
        name="resource-viewer",
    ),
    url(
        r"^api/resource/(?P<resource_uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/acquire/$",  # noqa
        ResourceAcquireView.as_view(),
        name="resource-viewer-acquire",
    ),
    url(r"^api/labels/$", ResourceLabelList.as_view(), name="resourcelabel-list"),
    url(r"^api/label/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        ResourceLabelDetail.as_view(),
        name="resourcelabel-detail",
    ),
    url(r"^api/resourcelists/$", ResourceListList.as_view(), name="resourcelist-list"),
    url(
        r"^api/resourcelist/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        ResourceListDetail.as_view(),
        name="resourcelist-detail",
    ),
    url(r"^api/resourcetypes/$", ResourceTypeList.as_view(), name="resourcetype-list"),
    url(
        r"^api/resourcetype/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        ResourceTypeDetail.as_view(),
        name="resourcetype-detail",
    ),
    url(r"^api/outputs/$", OutputList.as_view(), name="output-list"),
    url(
        r"^api/output/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        OutputDetail.as_view(),
        name="output-detail",
    ),
    url(r"^api/inputs/$", InputList.as_view(), name="input-list"),
    url(
        r"^api/input/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",
        InputDetail.as_view(),
        name="input-detail",
    ),
    url(
        r"^api/interactive/(?P<run_job_uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/acquire/$",  # noqa
        InteractiveAcquireView.as_view(),
        name="interactive-acquire",
    ),
    url(
        r"^api/interactive/(?P<run_job_uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/(?P<working_user_token>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/(?P<additional_url>.*)$",  # noqa
        InteractiveWorkingView.as_view(),
        name="interactive-working",
    ),
    url(
        r"^api/workflowjobcoordinatesets/$",
        WorkflowJobCoordinateSetList.as_view(),
        name="workflowjobcoordinateset-list",
    ),
    url(
        r"^api/workflowjobcoordinateset/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",  # noqa
        WorkflowJobCoordinateSetDetail.as_view(),
        name="workflowjobcoordinateset-detail",
    ),
    url(
        r"^api/workflowjobgroupcoordinatesets/$",
        WorkflowJobGroupCoordinateSetList.as_view(),
        name="workflowjobgroupcoordinateset-list",
    ),
    url(
        r"^api/workflowjobgroupcoordinateset/(?P<pk>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/$",  # noqa
        WorkflowJobGroupCoordinateSetDetail.as_view(),
        name="workflowjobgroupcoordinateset-detail",
    ),
    url(r"^api/auth/me/", AuthMeView.as_view(), name="auth-me"),
    url(
        r"^api/auth/register/",
        djoser_views.UserCreateView.as_view(),
        name="auth-register",
    ),
    url(r"^api/auth/token/", AuthTokenView.as_view(), name="auth-token"),
    url(
        r"^api/auth/reset-token/",
        djoser_views.TokenDestroyView.as_view(),
        name="auth-reset-token",
    ),
    url(
        r"^api/auth/change-password/",
        djoser_views.SetPasswordView.as_view(),
        name="auth-change-password",
    ),
    url(r"^api/ht/", include("health_check.urls")),
]

urlpatterns += format_suffix_patterns(api_patterns, allowed=["json", "html"])

# For serving stuff in debug mode only
if settings.DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
