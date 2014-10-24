from django.conf.urls import patterns, include, url, static
from django.conf import settings
from django.contrib import admin

from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token

from rodan.views.auth import SessionAuth
from rodan.views.auth import SessionStatus
from rodan.views.auth import SessionClose

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
from rodan.views.job import JobList
from rodan.views.job import JobDetail
from rodan.views.result import ResultList
from rodan.views.result import ResultDetail
from rodan.views.user import UserList
from rodan.views.user import UserDetail
from rodan.views.resultspackage import ResultsPackageList, ResultsPackageDetail
from rodan.views.connection import ConnectionList, ConnectionDetail
from rodan.views.outputport import OutputPortList, OutputPortDetail
from rodan.views.outputporttype import OutputPortTypeList, OutputPortTypeDetail
from rodan.views.inputport import InputPortList, InputPortDetail
from rodan.views.inputporttype import InputPortTypeList, InputPortTypeDetail
from rodan.views.resource import ResourceList, ResourceDetail
from rodan.views.output import OutputList, OutputDetail
from rodan.views.input import InputList, InputDetail
from rodan.views.resourceassignment import ResourceAssignmentList, ResourceAssignmentDetail

from rodan.views import interactive

# this will only run with the first request.
from rodan.startup import startup
startup()


urlpatterns = []

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += format_suffix_patterns(
    patterns('rodan.views.main',
        url(r'^browse/$', 'api_root'),
        url(r'^auth/token/$', obtain_auth_token),
        url(r'^auth/session/$', SessionAuth.as_view()),
        url(r'^auth/status/$', SessionStatus.as_view()),
        url(r'^auth/logout/$', SessionClose.as_view()),
        url(r'^$', 'home'),
        url(r'^projects/$', ProjectList.as_view(), name="project-list"),
        url(r'^project/(?P<pk>[0-9a-z\-]+)/$', ProjectDetail.as_view(), name="project-detail"),
        url(r'^workflows/$', WorkflowList.as_view(), name="workflow-list"),
        url(r'^workflow/(?P<pk>[0-9a-z\-]+)/$', WorkflowDetail.as_view(), name="workflow-detail"),
        url(r'^workflowjobs/$', WorkflowJobList.as_view(), name="workflowjob-list"),
        url(r'^workflowjob/(?P<pk>[0-9a-z\-]+)/$', WorkflowJobDetail.as_view(), name="workflowjob-detail"),
        url(r'^jobs/$', JobList.as_view(), name="job-list"),
        url(r'^job/(?P<pk>[0-9a-z\-]+)/$', JobDetail.as_view(), name="job-detail"),
        url(r'^results/$', ResultList.as_view(), name="result-list"),
        url(r'^result/(?P<pk>[0-9a-z\-]+)/$', ResultDetail.as_view(), name="result-detail"),
        url(r'^users/$', UserList.as_view(), name="user-list"),
        url(r'^user/(?P<pk>[0-9\-]+)/$', UserDetail.as_view(), name="user-detail"),
        url(r'^workflowruns/$', WorkflowRunList.as_view(), name="workflowrun-list"),
        url(r'^workflowrun/(?P<pk>[0-9a-z\-]+)/$', WorkflowRunDetail.as_view(), name="workflowrun-detail"),
        url(r'^runjobs/$', RunJobList.as_view(), name="runjob-list"),
        url(r'^runjob/(?P<pk>[0-9a-z\-]+)/$', RunJobDetail.as_view(), name="runjob-detail"),
        url(r'^resultspackages/$', ResultsPackageList.as_view(), name="resultspackage-list"),
        url(r'^resultspackage/(?P<pk>[0-9a-z\-]+)/$', ResultsPackageDetail.as_view(), name="resultspackage-detail"),
        url(r'^connections/$', ConnectionList.as_view(), name="connection-list"),
        url(r'^connection/(?P<pk>[0-9a-z\-]+)/$', ConnectionDetail.as_view(), name="connection-detail"),
        url(r'^outputporttypes/$', OutputPortTypeList.as_view(), name="outputporttype-list"),
        url(r'^outputporttype/(?P<pk>[0-9a-z/-]+)/$', OutputPortTypeDetail.as_view(), name="outputporttype-detail"),
        url(r'^outputports/$', OutputPortList.as_view(), name="outputport-list"),
        url(r'^outputport/(?P<pk>[0-9a-z/-]+)/$', OutputPortDetail.as_view(), name="outputport-detail"),
        url(r'^inputporttypes/$', InputPortTypeList.as_view(), name="inputporttype-list"),
        url(r'^inputporttype/(?P<pk>[0-9a-z/-]+)/$', InputPortTypeDetail.as_view(), name="inputporttype-detail"),
        url(r'^inputports/$', InputPortList.as_view(), name="inputport-list"),
        url(r'^inputport/(?P<pk>[0-9a-z/-]+)/$', InputPortDetail.as_view(), name="inputport-detail"),
        url(r'^resources/$', ResourceList.as_view(), name="resource-list"),
        url(r'^resource/(?P<pk>[0-9a-z/-]+)/$', ResourceDetail.as_view(), name="resource-detail"),
        url(r'^outputs/$', OutputList.as_view(), name="output-list"),
        url(r'^output/(?P<pk>[0-9a-z/-]+)/$', OutputDetail.as_view(), name="output-detail"),
        url(r'^inputs/$', InputList.as_view(), name="input-list"),
        url(r'^input/(?P<pk>[0-9a-z/-]+)/$', InputDetail.as_view(), name='input-detail'),
        url(r'^resourceassignments/$', ResourceAssignmentList.as_view(), name='resourceassignment-list'),
        url(r'^resourceassignment/(?P<pk>[0-9a-z/-]+)/$', ResourceAssignmentDetail.as_view(), name='resourceassignment-detail')
    )
)

urlpatterns += patterns('',
    url(r'^interactive/poly_mask/$', interactive.PolyMaskView.as_view()),
    url(r'^interactive/crop/$', interactive.CropView.as_view()),
    url(r'^interactive/binarise/$', interactive.BinariseView.as_view()),
    url(r'^interactive/despeckle/$', interactive.DespeckleView.as_view()),
    url(r'^interactive/rotate/$', interactive.RotateView.as_view()),
    url(r'^interactive/segment/$', interactive.SegmentView.as_view()),
    url(r'^interactive/luminance/$', interactive.LuminanceView.as_view()),
    url(r'^interactive/barlinecorrection/$', interactive.BarlineCorrectionView.as_view()),
    url(r'^interactive/pixel_segment/$', interactive.PixelSegmentView.as_view()),
)

# For serving stuff under MEDIA_ROOT in debug mode only
if settings.DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
