from django.db import models
import rodan.jobs


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
    is_required = models.BooleanField()

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
