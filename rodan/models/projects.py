import os

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

import rodan.jobs
from rodan.models.jobs import JobType
from rodan.utils import get_size_in_mb

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
    pk_name = 'project_id'

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('rodan.views.projects.view', [str(self.id)])

    # Takes in a User (not a RodanUser), returns true if the user created it
    def is_owned_by(self, user):
        return user.is_authenticated() and self.creator == user.get_profile()

    def get_percent_done(self):
        percent_done = sum(page.get_percent_done() for page in self.page_set.all())
        return percent_done / self.page_set.count() if self.page_set.count() else 0

    def get_divaserve_dir(self):
        return os.path.join(settings.MEDIA_ROOT,
                            "%d" % self.id,
                            'final')

    def is_partially_complete(self):
        Job = models.loading.get_model('rodan', 'Job')
        diva_job = Job.objects.get(pk='diva-preprocess')
        return any(page.get_percent_done() == 100 and page.workflow.jobitem_set.filter(job=diva_job).count() for page in self.page_set.all())

    def get_fake_progress(self):
        """
        Returns the real progress if the project has a description (in order
        to ensure that the newly-created Salzinnes project doesn't have a weird
        fake progress bar).
        """
        if self.description:
            return self.get_percent_done()
        else:
            return (hash(self.name) % 1000) / 10


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
    slug = models.CharField(max_length=20, primary_key=True)
    module = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    is_automatic = models.BooleanField()
    pk_name = 'job_slug'

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('rodan.views.jobs.view', [self.slug])

    def get_view(self, page):
        """
        Returns a tuple of the template to use and a context dictionary
        """
        return ('jobs/%s.html' % self.slug, self.get_object().get_context(page))

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

    project = models.ForeignKey(Project)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    jobs = models.ManyToManyField(Job, through='JobItem', null=True, blank=True)
    has_started = models.BooleanField(default=False)
    pk_name = 'workflow_id'

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('rodan.views.workflows.view', [str(self.id)])

    def get_percent_done(self):
        percent_done = sum(page.get_percent_done() for page in self.page_set.all())
        return percent_done / self.page_set.count() if self.page_set.count() else 0


class Page(models.Model):
    class Meta:
        app_label = 'rodan'
        unique_together = ('project', 'sequence')
        ordering = ['project', 'sequence']

    project = models.ForeignKey(Project)
    # Will only begin processing once a workflow has been specified
    workflow = models.ForeignKey(Workflow, null=True, blank=True)
    filename = models.CharField(max_length=50)
    tag = models.CharField(max_length=50, null=True, blank=True, help_text="Optional tag for the page. Sort of like a nickname.")
    # Used in conjunction with the @rodan_view decorator
    pk_name = 'page_id'
    sequence = models.IntegerField()

    # If the tag is defined, it returns that; otherwise, returns the filename
    def __unicode__(self):
        return self.tag or self.filename

    # Defines the hierarchy for generating breadcrumbs
    def get_parent(self):
        return self.project

    @models.permalink
    def get_absolute_url(self):
        return ('rodan.views.pages.view', [str(self.id)])

    def get_original_image_size(self):
        """
        Gets the size of the TIFF image that was originally uploaded.
        """
        return get_size_in_mb(os.path.getsize(self.get_latest_file_path('original')))

    def get_original_image_dimensions(self):
        # Hardcoding fake dimensions for now because it's easier and cheaper
        return {'width': 4414, 'height': 6993}

    @staticmethod
    def _get_thumb_filename(path, size):
        base_path, _ = os.path.splitext(path)
        return "%s_%s.%s" % (base_path, size, settings.THUMBNAIL_EXT)

    def _get_thumb_path(self, size, job):
        return os.path.join("%d" % self.project.id,
                            "%d" % self.id,
                            "%s" % job.slug if job is not None else '',
                            self._get_thumb_filename(self.filename, size))

    def _get_latest_file_path(self, file_type):
        """
        Helper method used by both get_file_url and get_file_path.
        Does not include the MEDIA_ROOT or MEDIA_URL.
        For getting the path to a file associated with a page.

        If the `latest` keyword argument is set to True, it will return the
        most recently created file of the specified type. Otherwise,
        """
        # Importing ResultFile directly would result in circular imports
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

        try:
            return files[0].filename
        except IndexError:
            return None

    def get_mei_url(self):
        return settings.MEDIA_URL + self._get_latest_file_path('mei')

    def get_latest_file_path(self, file_type):
        """
        Returns the absolute filepath to the latest result file creatd
        of the specified type. The `file_type` keyword argument is a string
        indicating the file extension (e.g. 'json', 'xml', 'tiff'). If no
        result files have been created of that type, then None will be
        returned.

        If the file_type is tiff and no jobs have been completed on this page,
        the original image file is returned (and so None will never be
        returned). It will also be returned if the file type is 'original'.
        """

        if file_type == 'page_number':
            # Needed for solr indexing. Really hacky, will fix eventually
            return self.sequence

        if file_type == 'project_id':
            # Same as above. Sorry.
            return self.project.id

        if file_type == 'prebin':
            if self.workflow.jobitem_set.count():
                for jobitem in self.workflow.jobitem_set.order_by('-sequence'):
                    if jobitem.job.get_object().output_type == JobType.IMAGE:
                        return self.get_job_path(jobitem.job, 'tiff')

        if file_type != 'original':
            latest_file_path = self._get_latest_file_path(file_type)

            if latest_file_path is not None:
                return os.path.join(settings.MEDIA_ROOT,
                                latest_file_path)

        if file_type == 'original' or file_type == 'prebin' or file_type == 'tiff':
            return os.path.join(settings.MEDIA_ROOT,
                                "%d" % self.project_id,
                                "%d" % self.id,
                                self.filename)

    def get_latest_thumb_url(self, size=settings.SMALL_THUMBNAIL):
        latest_file_path = self._get_latest_file_path('tiff')

        if latest_file_path is not None:
            file_path = self._get_thumb_filename(latest_file_path, size)
            # This is not actually a filepath but there are / issues otherwise
            return os.path.join(settings.MEDIA_URL,
                                file_path)
        else:
            return self.get_thumb_url(size, None)

    def get_pre_bin_image_url(self, size=settings.LARGE_THUMBNAIL):
        """
        Get the url to the latest pre-binarised image (i.e. the output of the
        step right before binarisation, or the latest step if binarisation is
        either not part of the workflow or has not yet been completed.
        """
        original = self.get_thumb_url(size=size)
        if self.workflow.jobitem_set.count():
            for jobitem in self.workflow.jobitem_set.order_by('-sequence'):
                if jobitem.job.get_object().output_type == JobType.IMAGE:
                    return self.get_thumb_url(size=size, job=jobitem.job)

        # Otherwise, just return the original
        return original

    def get_thumb_url(self, size=settings.SMALL_THUMBNAIL, job=None):
        return os.path.join(settings.MEDIA_URL,
                            self._get_thumb_path(size, job))

    def get_thumb_path(self, size=settings.SMALL_THUMBNAIL, job=None):
        """
        Get the absolute path to the thumbnail image.

        `size` is the width, in pixels, of the desired thumbnail image.
        `job` is the job object (either of type JobBase or a model).

        If you want to get the thumbnail for the latest job, use
        get_latest_image_path() and pass in the desired size as a keyword
        argument.
        """
        return os.path.join(settings.MEDIA_ROOT,
                            self._get_thumb_path(size=size, job=job))

    def _get_job_path(self, job, ext):
        """
        Returns the relative path to the file for the specified
        job and extension. 
        """
        basename, _ = os.path.splitext(self.filename)

        return os.path.join("%d" % self.project.id,
                            "%d" % self.id,
                            "%s" % job.slug,
                            "%s.%s" % (basename, ext))

    def get_job_path(self, job, ext):
        """
        Returns the absolute path to the file for the specified
        job and extension. Used when saving files (only).

        Job will never be None. To save original image thumbnails, use
        get_thumb_path.
        """
        basename, _ = os.path.splitext(self.filename)

        return os.path.join(settings.MEDIA_ROOT,
                            "%d" % self.project.id,
                            "%d" % self.id,
                            "%s" % job.slug,
                            "%s.%s" % (basename, ext))

    def get_pyramidal_tiff_path(self):
        """
        Because divaserve expects all the pyramidal tiff images for one
        project to be stored in the same directory.
        """
        return os.path.join(self.project.get_divaserve_dir(),
                            "%d.tiff" % self.sequence)

    def get_next_job_item(self, user=None):
        if not self.workflow:
            return None

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

    def start_next_job(self, user):
        next_job_item = self.get_next_job_item(user=user)
        # Create a new result only if there are none
        if next_job_item is not None and next_job_item.result_set.filter(page=self).count() == 0:
            Result = models.loading.get_model('rodan', 'Result')
            result = Result.objects.create(job_item=next_job_item, user=user, page=self)
            return result

    def start_next_automatic_job(self, user):
        next_job = self.get_next_job(user=user)
        if next_job is not None:
            next_job_obj = next_job.get_object()
            if next_job_obj.is_automatic:
                next_result = self.start_next_job(user)
                next_result.update_end_manual_time()
                next_job_obj.on_post(next_result.id, **next_job_obj.parameters)

    def get_percent_done(self):
        Result = models.loading.get_model('rodan', 'Result')
        num_complete = Result.objects.filter(page=self, end_total_time__isnull=False).count()
        try:
            num_jobs = self.workflow.jobitem_set.count()
            return (100 * num_complete) / num_jobs
        except (AttributeError, ZeroDivisionError):
            return 0

    def handle_image_upload(self, file):
        # Might need to fix the filename extension
        basename, _ = os.path.splitext(self.filename)
        self.filename = basename + '.tiff'
        self.save()

        image_path = self.get_latest_file_path('tiff')
        rodan.jobs.utils.create_dirs(image_path)

        with open(image_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Now generate thumbnails
        for thumbnail_size in settings.THUMBNAIL_SIZES:
            thumb_path = self.get_thumb_path(size=thumbnail_size)
            rodan.jobs.misc_tasks.create_thumbnails_task.delay(image_path, thumb_path, thumbnail_size)

    def is_job_complete(self, job_item):
        Result = models.loading.get_model('rodan', 'Result')
        return Result.objects.filter(job_item=job_item,
                                     page=self,
                                     end_total_time__isnull=False
                                     ).count()

    def reset_to_job(self, job):
        this_sequence = self.workflow.jobitem_set.get(job=job).sequence
        # Delete all the results whose jobitems have sequence >= this one
        results_to_delete = self.result_set.filter(job_item__sequence__gte=this_sequence)
        results_to_delete.delete()


class JobItem(models.Model):
    class Meta:
        app_label = 'rodan'
        unique_together = ('workflow', 'sequence')
        ordering = ['sequence']

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
