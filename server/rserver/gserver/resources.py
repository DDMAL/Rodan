from tastypie.resources import ModelResource
from rserver.gserver.models import Image, ImageTransformation

class MyModelResource(ModelResource):
	class Meta:
		queryset = MyModel.objects.all()
		allowed_methods = ['get']