from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^binarize/simple/(?P<page_id>\d+)', 'processing.views.simple_binarize_view'),
)