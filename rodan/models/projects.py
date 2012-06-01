from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from rodan.models.jobs import JobType

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

    The module is in the form 'rodan.jobs.binarisation.Binarise', where
    'binarisation.py' is a file under rodan/jobs, and Binarise is a class
    defined in that file.

    All instances of this model (i.e. rows in the database) are created after
    syncing the database (if they have not already been created), using the
    post_sync hook. They should not be added manually, via fixtures or
    otherwise.
    """
    class Meta:
        app_label = 'rodan'

    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=20)
    module = models.CharField(max_length=100, primary_key=True)

    def __unicode__(self):
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

    def get_latest_file(self, file_type):
        """
        To get the latest image: page.get_latest_file(JobType.IMAGE)

        Will return the original image if no image-generating jobs have
        been completed on the page.

        For now it's just the filename, not the absolute path. Still need
        to work out the directory structure.
        """
        # Because importing ResultFile would cause circular imports etc
        result_files = models.loading.get_model('rodan', 'ResultFile')

        # Don't worry about the query below. It works.
        result_files = result_files.objects.filter(result__page=self, result__job_item__workflow=self.workflow, result__end_total_time__isnull=False, result_type=file_type).order_by('-result__job_item__sequence').all()

        if result_files.count():
            # If there are any result_files of this type, return the latest
            return result_files[0]
        else:
            # If we're looking for an image, and no jobs have changed it
            # Then just return the original ...
            if file_type == JobType.IMAGE:
                return self.filename
            else:
                return None

    def get_next_job(self, user=None):
        """
        If user is None, it returns the next available job that has not yet
        been started. If the user is specified, it returns the next
        available job that has either not been started or that has been
        started by the specified user.
        """
        for job_item in self.workflow.jobitem_set.all():
            # Is there a result attached to this job item?
            page_results = job_item.result_set.filter(page=self)
            no_result = page_results.count() == 0

            if no_result:
                return job_item.job
            else:
                # There is a result. If the end time is empty and the user is the same ...
                first_result = page_results.all()[0]
                if first_result.end_total_time is None and first_result.user == user:
                    return job_item.job
                else:
                    continue


class JobItem(models.Model):
    class Meta:
        app_label = 'rodan'
        unique_together = ('workflow', 'sequence')

    workflow = models.ForeignKey(Workflow)
    job = models.ForeignKey(Job)
    sequence = models.IntegerField()

    def __unicode__(self):
        return "%s in workflow '%s' (step %d)" % (self.job, self.workflow, self.sequence)


class ActionParam(models.Model):
    class Meta:
        app_label = 'rodan'
    """Specifies the intended defaults for a job.
    """
    job_item = models.ForeignKey(JobItem)
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50)

    def __unicode__(self):
        return "%s: %s, for %s" % (job_item, key, value)


# Defines a post_save hook to ensure that a RodanUser is created for each User
def create_rodan_user(sender, instance, created, **kwargs):
    if created:
        RodanUser.objects.create(user=instance)

models.signals.post_save.connect(create_rodan_user, sender=User)
