from tastypie.resources import ModelResource
from gserver.models import Image, ImageTransformation

class ImageResource(ModelResource):
	class Meta:
		queryset = Image.objects.all()
		resource_name = 'entry'
		# allowed_methods = ['get']