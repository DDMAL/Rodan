from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^binarise/simple/(?P<page_id>\d+)', 'processing.views.simple_binarise_view'),
)