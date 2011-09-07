from tastypie.resources import ModelResource
from gserver.models import Image, ImageTransformation

class ImageResource(ModelResource):
	class Meta:
		queryset = Image.objects.all()
		resource_name = 'image'

class ImageTransformationResource(ModelResource):
	class Meta:
		queryset = ImageTransformation.objects.all()
		resource_name = 'it'