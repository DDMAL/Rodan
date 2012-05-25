from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'rodan.views.home'),
    url(r'^signup', 'rodan.views.signup'),
    url(r'^logout', 'rodan.views.logout_view'),
    url(r'^projects/', include('projects.urls')),
    url(r'^processing/', include('processing.urls')),
    url(r'^recognition/', include('recognition.urls')),
    url(r'^correction/', include('correction.urls')),
    url(r'^display/', include('display.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
