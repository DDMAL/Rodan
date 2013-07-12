from django.conf.urls import patterns, include, url, static
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

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
from rodan.views.page import PageList
from rodan.views.page import PageDetail
from rodan.views.job import JobList
from rodan.views.job import JobDetail
from rodan.views.result import ResultList
from rodan.views.result import ResultDetail
from rodan.views.user import UserList
from rodan.views.user import UserDetail
from rodan.views.classifier import ClassifierList
from rodan.views.classifier import ClassifierDetail
from rodan.views.pageglyphs import PageGlyphsList
from rodan.views.pageglyphs import PageGlyphsDetail


from rodan.views import interactive


urlpatterns = []

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
        url(r'^classifiers/$', ClassifierList.as_view(), name="classifier-list"),
        url(r'^classifier/(?P<pk>[0-9a-z\-]+)/$', ClassifierDetail.as_view(), name="classifier-detail"),
        url(r'^pageglyphs/$', PageGlyphsList.as_view(), name="pageglyphs-list"),
        url(r'^pageglyphs/(?P<pk>[0-9a-z\-]+)/$', PageGlyphsDetail.as_view(), name="pageglyphs-detail"),
    )
)

urlpatterns += patterns('',
        url(r'^interactive/crop/$', interactive.CropView.as_view()),
        url(r'^interactive/binarise/$', interactive.BinariseView.as_view()),
        url(r'^interactive/despeckle/$', interactive.DespeckleView.as_view()),
        url(r'^interactive/rotate/$', interactive.RotateView.as_view()),
        url(r'^interactive/segment/$', interactive.SegmentView.as_view()),
        url(r'^interactive/luminance/$', interactive.LuminanceView.as_view()),
        url(r'^interactive/barlinecorrection/$', interactive.BarlineCorrectionView.as_view()),
        url(r'^interactive/neon/$', interactive.NeonView.as_view()),
    )

urlpatterns += patterns('rodan.views.diva',
        url(r'^diva/data/$', 'divaserve')
    )

# Add neon urls only if neon jobs are installed.
try:
    from rodan.jobs.neon import urls
except ImportError as e:
    from rodan.settings import DEBUG
    if DEBUG:
        print "No neon job is installed. Neon urls will not be handled."
        print "The following exception was raised: ", e
else:
    urlpatterns += patterns('',
            url(r'^interactive/neon/$', interactive.NeonView.as_view()),
            url(r'^interactive/neon/edit/', include('rodan.jobs.neon.urls')),
    )

# Only add admin if it's enabled
if 'django.contrib.admin' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^admin/', include(admin.site.urls)),
    )

# For serving stuff under MEDIA_ROOT in debug mode only
if settings.DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
