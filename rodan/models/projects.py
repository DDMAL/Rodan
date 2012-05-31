from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class RodanUser(models.Model):
    class Meta:
        app_label = 'rodan'

    user = models.OneToOneField(User)
    affiliation = models.CharField(max_length=100)

    def __unicode__(self):
        return self.user.username


class Project(models.Model):
    class Meta:
        app_label = 'rodan'

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(RodanUser)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('rodan.views.projects.view', str(self.id))

    # Takes in a User (not a RodanUser), returns true if the user created it
    def is_owned_by(self, user):
        return user.is_authenticated() and self.creator == user.get_profile()


class Job(models.Model):
    """The slug is automatically generated from the class definition, but
    can be overridden by setting the 'slug' attribute. This is used for URL
    routing purposes.

    The name is also automatically generated from the class definition, but,
    again, can be overridden, this time by setting the 'name' attribute. This
    is used for display purposes.

    The module is in the form 'binarisation.Binarise', where 'binarisation.py'
    is a file under rodan/jobs, and Binarise is a class defined in that file.

    All instances of this model (i.e. rows in the database) are created after
    syncing the database (if they have not already been created), using the
    post_sync hook. They should not be added manually, via fixtures or
    otherwise.
    """
    class Meta:
        app_label = 'rodan'

    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=20)
    module = models.CharField(max_length=100)

    def __unicode__(self):
        # Return everything after the .
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('rodan.views.jobs.view', self.slug)

    def get_object(self):
        return jobs[self.module]


class Workflow(models.Model):
    class Meta:
        app_label = 'rodan'

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    jobs = models.ManyToManyField(Job, through='JobItem', null=True, blank=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('rodan.views.workflows.view', str(self.id))


class Page(models.Model):
    class Meta:
        app_label = 'rodan'

    project = models.ForeignKey(Project)
    # Will only begin processing once a workflow has been specified
    workflow = models.ForeignKey(Workflow, null=True)
    filename = models.CharField(max_length=50)
    tag = models.CharField(max_length=50, null=True, help_text="Optional tag for the page. Sort of like a nickname.")

    # If the tag is defined, it returns that; otherwise, returns the filename
    def __unicode__(self):
        return self.tag or self.filename

    @models.permalink
    def get_absolute_url(self):
        return ('rodan.views.pages.view', str(self.id))

    # Returns the path to a thumbnail of the image (size can be small or large)
    def get_image_url(self, size='small'):
        return '%(media_root)/%(project_id)/%(page_id)/%(size)/%(filename)' % {
            'media_root': settings.MEDIA_ROOT,
            'project_id': self.project.id,
            'page_id': self.id,
            'size': size,
            'filename': self.filename,
        }


class JobItem(models.Model):
    class Meta:
        app_label = 'rodan'

    workflow = models.ForeignKey(Workflow)
    job = models.ForeignKey(Job)
    sequence = models.IntegerField(unique=True)


class ActionParam(models.Model):
    class Meta:
        app_label = 'rodan'
    """Specifies the intended defaults for a job.
    """
    job_item = models.ForeignKey(JobItem)
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50)


# Defines a post_save hook to ensure that a RodanUser is created for each User
def create_rodan_user(sender, instance, created, **kwargs):
    if created:
        RodanUser.objects.create(user=instance)

models.signals.post_save.connect(create_rodan_user, sender=User)
