from rodan.models.job import Job
from django.conf import settings


def load_module():
    category = "Image Select"
    all_jobs = Job.objects.filter(category__exact=category)
    all_names = [j.name for j in all_jobs]
    if "rodan.jobs.utilities.image_select" not in all_names:
        pixel_types = [
            settings.ONEBIT,
            settings.GREYSCALE,
            settings.RGB,
            settings.GREY16
        ]

        image_select_job = {
            'name': "rodan.jobs.utilities.image_select",
            'arguments': {},
            'input_types': {},
            'output_types': {
                        'default': None,
                        'has_default': False,
                        'list_of': False,
                        'pixel_types': pixel_types,
                        'name': None
                    },
            'category': category,
            'is_enabled': True,
            'is_automatic': False,
            'is_required': False,
            'author': "Andrew Hankinson"
        }

        j = Job(**image_select_job)
        j.save()
