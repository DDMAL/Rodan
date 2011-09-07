from django.db import models
from uuidfield import UUIDField

class Image(models.Model):
	url = models.URLField()
	localpath = models.CharField(max_length = 255)
	id = UUIDField(auto = True, primary_key = True)
	pixel_type = models.IntegerField(max_length = 1)

	def __unicode__(self):
		return u"\nURL:{0} \nID:{1} \nPIXEL TYPE:{2}".format(self.url, self.id, self.pixel_type)

class ImageTransformation(models.Model):
	it = models.CharField(max_length = 255)
	id = UUIDField(auto = True, primary_key = True)

	def __unicode__(self):
		return u"\nTransformation:{0} \nID:{1}".format(self.it, self.id)




# http://www.vigliensoni.com/resources/vigliensoni_com.png