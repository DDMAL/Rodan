from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class RodanUser(models.Model):
    user = models.OneToOneField(User)
    affiliation = models.CharField(max_length=100)

    def __unicode__(self):
        return self.user.username

class Project(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250, blank=True, null=True)
    rodan_users = models.ManyToManyField(RodanUser)
    # The default workflow (can be overridden per page)
    workflow = models.ForeignKey('Workflow', null=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('projects.views.view', str(self.id))

class Page(models.Model):
    PIXELTYPE_CHOICES = (
        (0, "RGB"),
        (1, "grey_scale")
    )

    image_name = models.CharField(max_length=50)
    path_to_image = models.CharField(max_length=200) #full path + file name? or just directory location?
    pixel_type = models.IntegerField(choices=PIXELTYPE_CHOICES)
    width = models.IntegerField()
    height = models.IntegerField()
    size_in_kB = models.IntegerField()
    # Only NOT NULL if set to something other than the default
    workflow = models.ForeignKey('Workflow', null=True)
    project = models.ForeignKey(Project)

    def __unicode__(self):
        return "Page %s" % (self.path_to_image + self.image_name)

    def get_num_pixels(self):
        return self.width * self.height

    def get_size_in_mB(self):
        return (size_in_kB / 1024)

    @models.permalink
    def get_absolute_url(self):
        return ('projects.views.page_view', str(self.id))

class Job(models.Model):
    name = models.CharField(max_length=50)
    module = models.CharField(max_length=100)

    def __unicode__(self):
        return "Job %s (%s)" % (self.name, self.module)

    def get_absolute_url(self):
        return '/projects/job/%d' % self.id

class Workflow(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    jobs = models.ManyToManyField(Job, through='JobItem')

    def __unicode__(self):
        return "Workflow name: %s" % self.name

class JobItem(models.Model):
    workflow = models.ForeignKey(Workflow)
    job = models.ForeignKey(Job)
    sequence = models.IntegerField()

def create_rodan_user(sender, instance, created, **kwargs):
    if created:
        RodanUser.objects.create(user=instance)

# Register a handler for the post_save signal for User
# This ensures that a RodanUser is always created when a User is
# The demo user's RodanUser is created as a fixture
post_save.connect(create_rodan_user, sender=User)
