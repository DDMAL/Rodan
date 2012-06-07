from rodan.utils import remove_prefixes

# These are not actual Django models

class JobBase:
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

    def get_context(self):
        """
        Override this if you want to pass custom variables to the template.
        Will be accessible in the template as "context" (so if you return
        {'blah': 'blah'}, then it's accessible through {{ context.blah }} in
        the template.
        """
        return {}

    def on_post(self, result, **kwargs):
        """
        If you want to perform a custom action after submit that is
        not a celery task, override this
        """
        pass


class JobType:
    """
    IMAGE is a tuple used for Page.get_latest_file() (when you want to get
    the latest image and don't care what the colour palette is).

    The others are powers of two. To specify that a job's output type is
    MEI + a one-bit image, use IMAGE_ONEBIT + MEI. A ResultFile will always
    have only one type (e.g. MEI or IMAGE_ONEBIT, not both).
    """
    IMAGE_ONEBIT = 1
    IMAGE_GREY = 2
    IMAGE_RGB = 4
    JSON = 8
    XML = 16
    MEI = 32

    IMAGE = (IMAGE_ONEBIT, IMAGE_GREY, IMAGE_RGB)
