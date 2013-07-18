from rodan.models.job import Job
from django.conf import settings
from rodan.jobs.gamera.custom.border_removal.celery_task import AutoBorderRemovalTask, CropBorderRemovalTask

ONEBIT, GREYSCALE, RGB = settings.ONEBIT, settings.GREYSCALE, settings.RGB


def load_auto_border_removal():
    task_class = AutoBorderRemovalTask

    if not Job.objects.filter(job_name=task_class.name).exists():
        j = Job(job_name=task_class.name,
                author="Deepanjan Roy",
                description="Automatically tries to remove the border of a page. Non-interactive.",
                input_types={"default": None, "has_default": False, "list_of": False, "pixel_types": [GREYSCALE, ONEBIT, RGB], "name": "input"},
                output_types={"default": None, "has_default": False, "list_of": False, "pixel_types": [GREYSCALE, ONEBIT, RGB], "name": "output"},
                settings=task_class.settings,
                enabled=True,
                category="Border Removal",
                interactive=False
                )
        j.save()


def load_crop_border_removal():
    task_class = CropBorderRemovalTask

    if not Job.objects.filter(job_name=task_class.name).exists():
        j = Job(job_name=task_class.name,
                author="Deepanjan Roy",
                description="Manual masking crop. Uses the crop interface. Interactive.",
                input_types={"default": None, "has_default": False, "list_of": False, "pixel_types": [GREYSCALE, ONEBIT, RGB], "name": "input"},
                output_types={"default": None, "has_default": False, "list_of": False, "pixel_types": [GREYSCALE, ONEBIT, RGB], "name": "output"},
                settings=task_class.settings,
                enabled=True,
                category="Border Removal",
                interactive=True
                )

        j.save()


def load_module():
    load_auto_border_removal()
    load_crop_border_removal()
