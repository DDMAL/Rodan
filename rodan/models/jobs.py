from rodan.utils import remove_prefixes

# These are not actual Django models

class JobBase:
    name = ''
    slug = ''
    description = ''
    template = ''

    def get_name(self):
        return self.name or remove_prefixes(self.__class__.__name__)

    def get_slug(self):
        """If the child class defines a slug, use that; otherwise, take the
        class name and just convert it to lowercase.
        """
        return self.slug or self.get_name().lower()

class JobType:
    IMAGE = 1
    SEGMENTED_IMAGE = 2
    SEGMENTED_SHIT = 4
    OTHER = 8
