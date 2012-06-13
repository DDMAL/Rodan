import os

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

import rodan.jobs
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
    """
    The slug is automatically generated from the class definition, but
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

    def get_view(self):
        """
        Returns a tuple of the template to use and a context dictionary
        """
        return ('jobs/%s.html' % self.slug, self.get_object().get_context())

    def get_object(self):
        return rodan.jobs.jobs[self.module]

    def is_compatible(self, other_job):
        """
        Given another job, checks if it's compatible as the next job
        (based on input/output types)
        """
        return self.get_object().output_type == other_job.get_object().input_type

    def get_compatible_jobs(self):
        compatible_function = self.is_compatible
        return filter(compatible_function, Job.objects.all())


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
    workflow = models.ForeignKey(Workflow, null=True, blank=True)
    filename = models.CharField(max_length=50)
    tag = models.CharField(max_length=50, null=True, blank=True, help_text="Optional tag for the page. Sort of like a nickname.")

    # If the tag is defined, it returns that; otherwise, returns the filename
    def __unicode__(self):
        return self.tag or self.filename

    @models.permalink
    def get_absolute_url(self):
        return ('rodan.views.pages.view', str(self.id))

    # Returns the path to a thumbnail of the image (size can be small or large)
    def get_thumb_url(self, size='large'):
        # Remove the MEDIA_ROOT part
        path = self.get_latest_file('tiff')[len(settings.MEDIA_ROOT):]
        url = settings.MEDIA_URL + path + '_%s.jpg' % size
        return url

    def get_original_thumb_url(self, size='small'):
        path = self.get_path_to_image(size=size)[len(settings.MEDIA_ROOT):]
        url = settings.MEDIA_URL + path
        return url
        
    def get_path_to_image(self, size='large', job=None):
        return os.path.join(settings.MEDIA_ROOT,
                            "%d" % self.project.id,
                            "%d" % self.id,
                            "%s" % job.slug if job is not None else '',
                            "%s_%s.jpg" % (self.filename, size))

    def get_filename_for_job(self, job):
        #mediaroot/project/page/job/afile.ext
        return os.path.join(settings.MEDIA_ROOT,
                            "%d" % self.project.id,
                            "%d" % self.id,
                            "%s" % job.slug,
                            self.filename)

    def get_latest_file(self, file_type):
        """
        To get the latest image: page.get_latest_file('tiff')

        Will return the original image if no image-generating jobs have
        been completed on the page.

        For now it's just the filename, not the absolute path. Still need
        to work out the directory structure.

        You can pass in either a tuple of file types or just one.
        """

        # Because importing ResultFile would cause circular imports etc
        file_manager = models.loading.get_model('rodan', 'ResultFile').objects

        """
        The query below selects all the result files that match the following criteria:

        * The page of the result is the current page
        * The workflow that the result's job item belongs to is this page's
        * The result's end_total_time field is not null (so, job is complete)
        * The file type is the desired type

        It is then ordered by result's job item's sequence in the workflow.
        This is so that we get the latest file of the type we want.
        """
        files = file_manager.filter(result__page=self,
                                    result__job_item__workflow=self.workflow,
                                    result__end_total_time__isnull=False,
                                    result_type=file_type) \
                                    .order_by('-result__job_item__sequence') \
                                    .all()

        if files.count():
            # If there are any result_files of this type, return the latest
            return files[0].filename
        else:
            # If we're looking for an image, and no jobs have changed it
            # Then just return the original ...
            if file_type == 'tiff' or file_type == 'png':
                # If there is a filename, return the ABSOLUTE path
                return os.path.join(settings.MEDIA_ROOT,
                                    "%d" % self.project.id,
                                    "%d" % self.id,
                                    self.filename)
            else:
                return None

    def get_next_job_item(self, user=None):
        for job_item in self.workflow.jobitem_set.all():
            page_results = job_item.result_set.filter(page=self)
            no_result = page_results.count() == 0

            if no_result:
                return job_item
            else:
                first_result = page_results.all()[0]
                manual_not_done = first_result.end_manual_time is None
                automatic_not_done = first_result.end_total_time is None
                if manual_not_done and first_result.user == user:
                    return job_item
                elif automatic_not_done:
                    # This job is still processing - return None
                    return None

    def get_next_job(self, user=None):
        """
        If user is None, it returns the next available job that has not yet
        been started. If the user is specified, it returns the next
        available job that has either not been started or that has been
        started by the specified user.
        """
        next_job_item = self.get_next_job_item(user=user)
        return next_job_item.job if next_job_item is not None else None

    def start_next_job(self, user=None):
        next_job_item = self.get_next_job_item(user=user)
        # Create a new result only if there are none
        if next_job_item is not None and next_job_item.result_set.filter(page=self).count() == 0:
            Result = models.loading.get_model('rodan', 'Result')
            result = Result.objects.create(job_item=next_job_item, user=user, page=self)

    def get_percent_done(self):
        Result = models.loading.get_model('rodan', 'Result')
        num_complete = Result.objects.filter(page=self, end_total_time__isnull=False).count()
        num_jobs = self.workflow.jobitem_set.count()
        return (100 * num_complete) / num_jobs


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
    """
    Specifies the intended defaults for a job.
    """
    class Meta:
        app_label = 'rodan'

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
