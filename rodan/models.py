from django.db import models
from django.contrib.auth.models import User
from views import *
from django.utils import *

#this model is to extend the default user behaviour if we need additional information such as avatar
class RodanUser(models.Model):
	user = models.OneToOneField(User)
	affiliation = models.CharField(max_length=100)

class Project(models.Model):
	proj_name = models.CharField(max_length=50)

	rodan_users = models.ManyToManyField(RodanUser)

class Page(models.Model):
	PIXELTYPE_CHOICES = (
	(0,"RGB"),
	(1,"grey_scale"))

	page_name = models.CharField(max_length=50) #do pages have more meaningful names than the actual filename????
	path_to_image = models.CharField(max_length=200) #full path + file name? or just directory location?
	file_extension = models.CharField(max_length=5)
	pixel_type = models.IntegerField(choices=PIXELTYPE_CHOICES)
	width = models.IntegerField()
	height = models.IntegerField()
	size_in_kB = models.IntegerField()

	project = models.ForeignKey(Project)

	def __unicode__(self):
		return "Page %s" % self.page_name

	def get_num_pixels(self):
		return self.width * self.height

	def get_size_in_mB(self):
		return (size_in_kB / 1024)
		

class Workflow(models.Model):
	wf_name = models.CharField(max_length=50)
	wf_description = models.CharField(max_length=250)

	project = models.ForeignKey(Project)

	def __unicode__(self):
		return "Workflow name: %s" % self.wf_name


class Result(models.Model):
	start_time = models.DateTimeField(auto_now_add=True)
	end_time = models.DateTimeField()

	work_flow = models.ForeignKey(Workflow)
	page = models.OneToOneField(Page)

'''
class Result(models.Model):
	RESULT_TYPES=(
	("BI","Binarize"),
	("RO","Rotate"))

	work_flow = models.ForeignKey(Workflow)
	result_type = models.CharField(max_length=2,choices=RESULT_TYPES)
'''

class Rotate(models.Model):
	rotation_value = models.IntegerField()

	result = models.OneToOneField(Result)

	def __unicode__(self):
		return "Rotate Result w/ rotation_value=%s" % self.rotation_value

'''
class Crop(Job):


class Segmentation(Job):


class SegCorrection(Job):
	def do_stuff(self):
		return seg_correct_view
'''
#inherits the default behaviour and attributes from job, and adds additional information specific to this type of relationship
class Binarize(models.Model):
	#TO DO: find possible parameters for a binarize job
	#perhaps extend this as well for different types of binarization jobs??
	threshold_value = models.IntegerField()

	result = models.OneToOneField(Result)

	def __unicode__(self):
		return "Binarize Result w/ threshold_value=%s" % self.threshold_value