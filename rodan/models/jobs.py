from django.db.models.loading import get_model
from celery.task import task
from rodan.utils import remove_prefixes

# These are not actual Django models

class JobBase:
    is_automatic = False
    name = ''
    slug = ''
    description = ''
    template = ''
    """A dict of parameters to pass to a celery task"""
    parameters = {}
    """The celery task to execute"""
    task = None

    def get_name(self):
        return self.name or remove_prefixes(self.__class__.__name__)

    def get_slug(self):
        """If the child class defines a slug, use that; otherwise, take the
        class name and just convert it to lowercase.
        """
        return self.slug or self.get_name().lower()

    def get_context(self, page):
        """
        Override this if you want to pass custom variables to the template.
        Will be accessible in the template as "context" (so if you return
        {'blah': 'blah'}, then it's accessible through {{ context.blah }} in
        the template.
        """
        return {}

    def on_post(self, result_id, **kwargs):
        """
        If you want to perform a custom action after submit that is
        not a celery task, override this
        """
        self.task.delay(result_id, **kwargs)


class ManualJobBase(JobBase):
    def on_post(self, result_id, **kwargs):
        """
        Start the next automatic job.

        ManualJobBase should be used when there is no celery task required
        (and so there is no need to delay anything).
        """
        Result = get_model('rodan', 'Result')
        result = Result.objects.get(pk=result_id)
        result.page.start_next_automatic_job(result.user)


class JobType:
    """
    I will put in a nice descriptive docstring very very soon

    For now, note that all main types are prime and subtypes are multiples of
    the parent type.
    """
    IMAGE = 1
    BINARISED_IMAGE = 2
    POLYGON_JSON = 3
    CLASSIFY_XML = 4
    MEI = 5
    SEGMENTED_IMAGE = 6
    NEUME_IMAGE = 7
    RANKED_IMAGE = 8
    PITCH_JSON = 9
