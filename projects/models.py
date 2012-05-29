from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class RodanUser(models.Model):
    user = models.OneToOneField(User)
    affiliation = models.CharField(max_length=100)

    def __unicode__(self):
        return self.user.username

class Job(models.Model):
    MODULE_CHOICES = (
        ('BI','Binarise'),
        ('RO','Rotate')
    )

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    module = models.CharField(max_length=100,choices=MODULE_CHOICES)

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

class Project(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250, blank=True, null=True)
    rodan_user = models.ForeignKey(RodanUser)
    # The default workflow (can be overridden per page)
    workflow = models.ForeignKey(Workflow, null=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('projects.views.view', str(self.id))

    # Pass it a regular user (NOT a rodan user)
    def is_owned_by(self, user):
        if user.is_authenticated():
            return (self.rodan_user.id == user.id)
            #return self.rodan_user.filter(id=user.get_profile().id).exists()
        else:
            return False

class Page(models.Model):
    # Could be just the filename, or something more description
    image_name = models.CharField(max_length=50)
    # Full path to the image eventually, just the filename for now
    path_to_image = models.CharField(max_length=200)

    # Only NOT NULL if set to something other than the default
    workflow = models.ForeignKey(Workflow, null=True)
    project = models.ForeignKey(Project)

    def __unicode__(self):
        return self.image_name

    @models.permalink
    def get_absolute_url(self):
        return ('projects.views.page_view', str(self.id))

    def get_image_url(self):
        return 'http://rodan.simssa.ca/images/%d/%d/thumbs/0.jpg' % (self.project.id, self.id)

def create_rodan_user(sender, instance, created, **kwargs):
    if created:
        RodanUser.objects.create(user=instance)

# Register a handler for the post_save signal for User
# This ensures that a RodanUser is always created when a User is
# The demo user's RodanUser is created as a fixture
post_save.connect(create_rodan_user, sender=User)
