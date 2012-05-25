from django.db import models
from django.contrib.auth.models import User


#this model is to extend the default user behaviour if we need additional information such as avatar
class RodanUser(models.Model):
	user = models.OneToOneField(User)
	affiliation = models.CharField(max_length=100)

class Project(models.Model):
	proj_name = models.CharField(max_length=50)
	proj_description = models.CharField(max_length=250)

	rodan_users = models.ManyToManyField(RodanUser)