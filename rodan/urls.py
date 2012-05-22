from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'rodan.views.main'),
    url(r'^projects/', include('projects.urls')),
    url(r'^processing/', include('processing.urls')),
    url(r'^recognition/', include('recognition.urls')),
    url(r'^correction/', include('correction.urls')),
    url(r'^display/', include('display.urls')),
)
