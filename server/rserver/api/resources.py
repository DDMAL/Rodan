from tastypie.resources import ModelResource
from rserver.gserver.models import MyModel

class MyModelResource(ModelResource):
	class Meta:
		queryset = MyModel.objects.all()
		allowed_methods = ['get']