from django.conf.urls.defaults import patterns, include, url
from tastypie.api import Api
from api.api import ProjectResource, DocumentResource, PageResource
from api.api import ImageResource, TranscriptionResource, WorkflowResource, TaskStatusResource
from api.api import TaskResource, QueueResource, UserProfileResource, WorkflowStepResource
from rserver.gserver.resources import ImageResource, ImageTransformationResource

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(ProjectResource())
v1_api.register(DocumentResource())
v1_api.register(PageResource())
v1_api.register(ImageResource())
v1_api.register(TranscriptionResource())
v1_api.register(WorkflowResource())
v1_api.register(WorkflowStepResource())
v1_api.register(TaskResource())
v1_api.register(TaskStatusResource())
v1_api.register(QueueResource())
v1_api.register(UserProfileResource())

image_resource = ImageResource()
imagetransformation_resource = ImageTransformationResource()

urlpatterns = patterns('',
    #api
    (r'^api/', include(v1_api.urls)),
    
    
    # Examples:
    # url(r'^$', 'rserver.views.home', name='home'),
    # url(r'^rserver/', include('rserver.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    (r'^gserver/', include(image_resource.urls)),
    (r'^gserver/', include(imagetransformation_resource.urls)),
)
